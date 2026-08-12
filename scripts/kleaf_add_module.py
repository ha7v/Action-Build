#!/usr/bin/env python3
"""Declare an extra module output in selected Kleaf common-kernel targets."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


class BuildFileError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-file", type=Path, required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--target", action="append", required=True)
    return parser.parse_args()


def string_literal(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def unique_mapping_entry(mapping: ast.Dict, key: str, context: str) -> ast.AST:
    matches = [
        value
        for entry_key, value in zip(mapping.keys, mapping.values)
        if string_literal(entry_key) == key
    ]
    if len(matches) != 1:
        raise BuildFileError(
            f"Expected exactly one {key!r} entry in {context}, found {len(matches)}"
        )
    return matches[0]


def find_target_configs(tree: ast.AST) -> ast.Dict:
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "define_common_kernels"
    ]
    if len(calls) != 1:
        raise BuildFileError(
            f"Expected exactly one define_common_kernels() call, found {len(calls)}"
        )

    values = [keyword.value for keyword in calls[0].keywords if keyword.arg == "target_configs"]
    if len(values) != 1 or not isinstance(values[0], ast.Dict):
        raise BuildFileError("target_configs must be one inline dictionary")
    return values[0]


def expression_end_offset(content: str, node: ast.AST) -> int:
    if node.end_lineno is None or node.end_col_offset is None:
        raise BuildFileError("Python parser did not report the expression end position")

    lines = content.splitlines(keepends=True)
    line = lines[node.end_lineno - 1]
    # AST columns are UTF-8 byte offsets; convert them to a character offset.
    column = len(line.encode("utf-8")[: node.end_col_offset].decode("utf-8"))
    return sum(map(len, lines[: node.end_lineno - 1])) + column


def plan_insertions(
    content: str, module: str, targets: list[str]
) -> tuple[list[int], list[str]]:
    try:
        tree = ast.parse(content)
    except SyntaxError as error:
        raise BuildFileError(f"Cannot parse BUILD file: {error}") from error

    target_configs = find_target_configs(tree)
    insertions: list[int] = []
    unchanged: list[str] = []

    for target in targets:
        target_config = unique_mapping_entry(target_configs, target, "target_configs")
        if not isinstance(target_config, ast.Dict):
            raise BuildFileError(f"Target {target!r} must be an inline dictionary")

        outputs = unique_mapping_entry(
            target_config, "module_implicit_outs", f"target {target!r}"
        )
        occurrences = sum(
            string_literal(node) == module for node in ast.walk(outputs)
        )
        if occurrences > 1:
            raise BuildFileError(f"Module {module!r} is duplicated in target {target!r}")
        if occurrences == 1:
            unchanged.append(target)
        else:
            insertions.append(expression_end_offset(content, outputs))

    return insertions, unchanged


def main() -> None:
    args = parse_args()
    if len(set(args.target)) != len(args.target):
        raise SystemExit("Duplicate --target argument")
    if not args.build_file.is_file():
        raise SystemExit(f"BUILD file not found: {args.build_file}")

    content = args.build_file.read_text()
    try:
        insertions, _ = plan_insertions(content, args.module, args.target)
        addition = f" + [{json.dumps(args.module)}]"
        for offset in sorted(insertions, reverse=True):
            content = content[:offset] + addition + content[offset:]

        remaining, verified = plan_insertions(content, args.module, args.target)
        if remaining or set(verified) != set(args.target):
            raise BuildFileError("Post-edit verification failed")
    except BuildFileError as error:
        raise SystemExit(f"Kleaf module adaptation failed: {error}") from error

    if insertions:
        args.build_file.write_text(content)
        print(f"Declared {args.module} for: {', '.join(args.target)}")
    else:
        print(f"Already declared {args.module} for: {', '.join(args.target)}")


if __name__ == "__main__":
    main()
