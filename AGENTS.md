# 项目维护共识

本仓库是 `Numbersf/Action-Build`（官方项目） 的 fork。

`ha7v/oppo_oplus_realme_sm8650`、`ha7v/oppo_oplus_realme_sm8750` （功能上游）以及其他功能上游仓库只能作为功能和代码参考，不能作为本仓库的内核基线。必须保留官方设备 manifest、官方 `kernel_platform/common`、设备原有的 msm-kernel/modules、device tree 和编译方式；
禁止切换到 cctv18 或其他 common fork，禁止固定或替换为其 common commit。

## 本 fork 的本地改进

本 fork 与 DroidSpaces 相关的本地改进只有一项：

- `DROID_SPACES=extend`：在官方原版 DroidSpaces `standard` 支持上增加 `extend` 功能。

`BUILTIN_KSU=false` 是独立的构建选项，不属于 DroidSpaces `standard` 或 `extend` 的实现范围。

重点维护设备：

- 一加平板 Pro：SM8650，`android14-6.1`；
- 一加 13：SM8750，`android15-6.6`。

其他设备、官方编译链和无关选项保持原有行为；合并上游改动时必须保留上述两项本地改进，以及自定义编译用户和主机名功能。

## DroidSpaces 边界

### standard

`standard` 完全采用官方原版实现，不属于本 fork 的维护范围，也不属于本 fork 的 `extend`
增量。官方原版的 SysV IPC KABI、Midas、NTSYNC、namespace、IPC、devtmpfs、POSIX mqueue、
网络配置及其编译方式均应保持原样。

本 fork 不重写、替换、固定或清理 `standard` 的实现；合并改动时以官方 `standard` 行为为准。

### extend

`extend` 只增加：

- 本仓库内的 EVDI 虚拟 DRM/KMS 驱动，启用 `CONFIG_DRM_LINDROID_EVDI=y`；
- `CONFIG_BT_HCIVHCI=y`；当前为内置功能，不生成 `hci_vhci.ko`，不得添加其 Kleaf
  输出声明；
- `CONFIG_STATIC_USERMODEHELPER=n`。

extend 的源码和必要集成改动必须进入本仓库并按 KMI 管理。不得顺带引入另一个项目的
common fork、固定 commit、无关补丁、无关基线或无关功能，也不得改变官方 `standard` 的行为。

## 工作流、脚本和补丁纪律

- 所有新增或修改的工作流、脚本、补丁和工具必须来自触发构建的同一提交。
- CI 不得运行时克隆本仓库上游或从功能上游 `main` 下载、替换官方 common、源码或补丁。
- 补丁失败、产生 reject、重复应用或目标文件缺失时必须显式失败；禁止使用 `|| true` 掩盖。
- 复杂解析和文件变换必须放入独立脚本，不继续扩大工作流内联代码。
- 新增或修改的 extend 代码不得改变官方 `standard` 或其他设备的原有行为。

## CI 约定

- `easimon/maximize-build-space` 必须在 `actions/checkout` 前执行；
- 本仓库固定 checkout 到 `kernel_workspace/Action-Build`；
- 内核源码及 repo 管理的项目位于同级 `kernel_workspace/`；
- 引用本仓库文件时使用 `kernel_workspace/Action-Build`。

## 验证要求

- 通用修改：运行 `git diff --check`；
- 修改 Python 脚本：对实际修改的脚本运行 `python3 -m py_compile`；
- 修改工作流：解析 YAML，并检查关键 `run` 脚本；
- 修改 DroidSpaces `extend` 或其 KMI 集成逻辑：分别用 `android14-6.1` 和 `android15-6.6`
  的代表性结构验证；
- 分别记录补丁应用、编译、产物检查和设备启动结果；编译成功不等于可启动。
