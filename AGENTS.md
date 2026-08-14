# 项目长期共识

## 项目目标

本 fork 只维护两个主要本地改进：

1. `BUILTIN_KSU=false`：完全跳过内置 KernelSU；
2. `DROID_SPACES=extend`：在本仓库 `standard` 基础上增加 extend 独有功能。

维护设备：一加平板 Pro（SM8650，`android14-6.1`）和一加 13（SM8750，`android15-6.6`）。其他设备、官方编译链和无关选项保持原有行为。

## 内核基线

- 始终使用官方设备 manifest 和官方 `kernel_platform/common`。
- 保留设备原有的 msm-kernel、modules、device tree 和编译方式。
- 禁止切换到 cctv18 的 common fork 或固定其 commit。
- 上游作者的仓库只能作为功能和代码来源，不能作为本项目内核基线。

原因：上游维护的是已经改过 KABI 槽位和实现的 common fork；本项目采用官方 common + 本地补丁，二者不可等价替换。

## 功能边界

### standard

standard 基础包括 SysV IPC KABI 适配、Midas 修复、NTSYNC 兼容，以及容器所需的 namespace、IPC、devtmpfs、POSIX mqueue 和网络配置。

这些不是 extend 增量。SysV KABI 不得继续使用工作流中基于 `grep`/`sed` 猜槽位的复杂逻辑，应改为按 KMI 管理的静态补丁。

### extend

extend 只增加：

- EVDI 虚拟 DRM/KMS 驱动，启用 `CONFIG_DRM_LINDROID_EVDI=y`；
- `CONFIG_BT_HCIVHCI` 及实际生成的 `hci_vhci.ko` Kleaf 输出声明；
- `CONFIG_STATIC_USERMODEHELPER=n`。

不得顺便引入另一个项目的 common fork、固定 commit 或无关专用补丁。官方 common + standard 是已知可启动基线，extend 必须只验证自己的增量。

## 实现与同步纪律

- 所有工作流、脚本、补丁和工具必须来自触发构建的同一提交。
- extend 补丁必须进入本仓库，按 KMI/官方 common 版本管理；禁止运行时从上游 `main` 下载。
- 补丁失败、产生 reject 或重复应用必须显式失败，禁止用 `|| true` 掩盖。
- 基线分支为 `upstream/KernelSU`（`Numbersf/Action-Build`），通过 Git merge 同步；上游同步提交与本地功能提交分开。
- 合并冲突时保留可选内置 KernelSU、自定义编译用户/主机名、DroidSpaces extend 和 `scripts/kleaf_add_module.py` 适配。
- 复杂解析或文件变换放进独立脚本，不继续扩大工作流内联代码。

## CI 约定

- `easimon/maximize-build-space` 必须在 `actions/checkout` 前执行。
- 当前仓库固定检出到 `kernel_workspace/Action-Build`。
- 内核源码及 repo 管理项目位于同级 `kernel_workspace/`；引用本仓库文件使用 `kernel_workspace/Action-Build`。
- CI 不在运行时另行克隆上游 Action-Build。

## 验证

```sh
git diff --check
python3 -m py_compile scripts/kleaf_add_module.py
```

修改工作流时解析 YAML；修改 Kleaf helper 时使用 6.1 和 6.6 的代表性 `BUILD.bazel` 测试，并确认重复执行幂等。必须区分补丁应用、编译、产物检查和设备启动结果；编译成功不等于可启动。
