# 远端构建失败修复说明

## 故障原因

远端构建在 `Apply DROID_SPACES` 阶段失败，尚未进入内核编译。错误是：

```text
python3: can't open file '/home/runner/work/Action-Build/Action-Build/scripts/kleaf_add_module.py'
```

原因是 `easimon/maximize-build-space` 会重新挂载 `$GITHUB_WORKSPACE`。原工作流先执行 `checkout`，再执行该步骤，导致已检出的仓库内容被覆盖。之后工作流又在 `kernel_workspace/Action-Build` 临时克隆上游仓库，形成了当前仓库与上游仓库混用；新增的 `kleaf_add_module.py` 不在上游副本中，因此找不到。

## 修复内容

- 将 `Maximize Build Space` 调整到 `Checkout` 之前。
- 将当前触发构建的提交检出到 `kernel_workspace/Action-Build`。
- 删除构建过程中临时克隆 `Numbersf/Action-Build` 的逻辑。
- 修正 DroidSpaces Kleaf helper 的路径，使其与其他脚本、补丁使用同一份当前提交内容。
- 在根目录增加 `AGENTS.md`，记录上游同步、CI 目录和本地功能维护约束，便于后续合并上游时减少冲突。

## 验证

- 工作流 YAML 可解析。
- Python helper 编译检查通过。
- 6.1 和 6.6 的代表性 `BUILD.bazel` 均验证通过。
- helper 重复执行保持幂等，不会重复添加模块输出。
- 修复提交：`27bf916`。
- 修复后已触发 `oneplus_pad_pro_b` 和 `oneplus_13_b` 两个机型的构建。
