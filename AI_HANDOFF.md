# AI 短期交接

## 当前状态

- 已移除 extend 时切换到 cctv18 common 固定 commit 的工作流代码。
- 当前仍使用官方 manifest/common。
- extend 的正确实现尚未完成。
- 工作流仍有两处待重构：复杂 SysV KABI `sed`，以及运行时下载 EVDI 补丁。
- `BUILD_FIX_SUMMARY.md` 是已有记录，保留不改。

## 已知结果

- 官方 common + 本仓库 standard：已知可启动。
- 平板 Pro extend：编译成功，但实际刷入后卡第一屏/黑屏。
- 一加 13 extend：编译成功但尚未刷入，不能称为已验证启动。
- EVDI 是重点排查对象，但尚未证明是唯一根因。

## 下一步

1. 在官方 SM8650/SM8750 common 上检查并重做 standard 的静态 KABI 补丁。
2. 从 cctv18 项目提取 EVDI 代码，但针对官方 common 重新生成并纳入本仓库的 KMI 版本化补丁。
3. extend 只应用 EVDI 补丁和三项配置：
   - `CONFIG_DRM_LINDROID_EVDI=y`
   - `CONFIG_BT_HCIVHCI`
   - `CONFIG_STATIC_USERMODEHELPER=n`
4. 补丁失败必须终止；不使用远程可变补丁、固定 common commit 或 `|| true`。
5. 先做补丁检查、最终配置核对、Kleaf/helper 测试和编译；不要无必要地再次进行完整基线构建。

## 禁止回退

- 不恢复 common fork/固定 commit；
- 不继续堆叠 KABI `grep`/`sed` 分支；
- 不把 standard 内容重复算作 extend；
- 不把编译成功写成设备启动成功。
