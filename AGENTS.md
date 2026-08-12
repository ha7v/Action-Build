# 项目维护约束

## 上游同步

- 基线分支为 `upstream/KernelSU`（`Numbersf/Action-Build`），通过 Git merge 同步上游。
- 上游同步提交与本地功能修改分开，避免大范围重排或格式化工作流，减少合并冲突。
- CI 不在运行时另行克隆上游 Action-Build；工作流、脚本、补丁和工具必须来自触发构建的同一提交。

## CI 目录约定

- `easimon/maximize-build-space` 必须在 `actions/checkout` 前执行，否则新挂载会覆盖已检出的文件。
- 当前仓库固定检出到 `kernel_workspace/Action-Build`。
- 内核源码及 `repo` 管理的项目位于同级 `kernel_workspace/` 下；引用本仓库文件时使用 `kernel_workspace/Action-Build` 路径。

## 本地功能

合并上游冲突时应保留以下本地功能：

- 可选内置 KernelSU；
- 自定义内核编译用户和主机名；
- DroidSpaces 扩展模式；
- `scripts/kleaf_add_module.py` 对 DroidSpaces Kleaf 模块输出的适配。

复杂的解析或文件变换应放在独立脚本中，不要继续扩大工作流内联代码。

## 修改后验证

```sh
git diff --check
python3 -m py_compile scripts/kleaf_add_module.py
```

修改工作流时还需验证 YAML 可解析；修改 Kleaf helper 时需使用 6.1 和 6.6 的代表性 `BUILD.bazel` 测试，并确认重复执行不会产生额外修改。
