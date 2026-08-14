# 项目上下文

本仓库是 `Numbersf/Action-Build` 的 fork。`ha7v/oppo_oplus_realme_sm8650` 和
`ha7v/oppo_oplus_realme_sm8750` 仅作为功能参考，不能作为本仓库的内核基线；禁止切换到
其他 common fork 或固定其 commit。

本 fork 只维护两项本地改进：

- `BUILTIN_KSU=false`：完全跳过内置 KernelSU；
- `DROID_SPACES=extend`：在已验证可正常使用的官方 DroidSpaces `standard` 支持上增加扩展功能。

维护重点为一加平板 Pro（SM8650，`android14-6.1`）和一加 13（SM8750，`android15-6.6`）。
保留官方设备 manifest、官方 `kernel_platform/common`、设备原有的 msm-kernel/modules、
device tree 和编译方式；其他设备及原有功能保持原行为。

## DroidSpaces 边界

`standard` 是基线，不属于 extend 增量：包括按 KMI 管理的 SysV IPC KABI 补丁、Midas 修复、
NTSYNC 兼容，以及容器所需的 namespace、IPC、devtmpfs、POSIX mqueue 和网络配置。

`extend` 只增加：

- 本仓库内的 EVDI 虚拟 DRM/KMS 驱动，启用 `CONFIG_DRM_LINDROID_EVDI=y`；
- `CONFIG_BT_HCIVHCI=y`；当前为内置功能，不生成 `hci_vhci.ko`，不得添加其 Kleaf 输出声明；
- `CONFIG_STATIC_USERMODEHELPER=n`。

extend 的源码和补丁必须进入本仓库并按 KMI 管理，禁止运行时从功能上游 `main` 下载或替换官方
common。新增 extend 代码不得顺带引入无关补丁、基线或功能。

## 本 fork 新增代码的约束

以下约束只适用于本 fork 新增或修改的工作流、脚本、补丁和工具，不要求为上游原有逻辑做无关重构：

- 所有新增工作流、脚本、补丁和工具必须来自触发构建的同一提交；CI 不得运行时克隆本仓库上游。
- 新增补丁失败、产生 reject 或重复应用时必须显式失败，禁止用 `|| true` 掩盖。
- 复杂解析和文件变换放进独立脚本，不继续扩大工作流内联代码。
- 合并上游改动时保留上述两项本地改进，以及自定义编译用户/主机名功能。

## CI 约定

- `easimon/maximize-build-space` 必须在 `actions/checkout` 前执行；
- 本仓库固定 checkout 到 `kernel_workspace/Action-Build`；
- 内核源码及 repo 管理的项目位于同级 `kernel_workspace/`，引用本仓库文件使用
  `kernel_workspace/Action-Build`。

## 验证

- 通用修改：`git diff --check`；
- 修改 Python 脚本：对实际修改的脚本运行 `python3 -m py_compile`；
- 修改工作流：解析 YAML；
- 修改 DroidSpaces/KMI 逻辑：分别用 `android14-6.1` 和 `android15-6.6` 的代表性结构验证；
- 区分补丁应用、编译、产物检查和设备启动结果；编译成功不等于可启动。
