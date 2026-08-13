# AI 短期交接

## 当前状态

- 已移除 extend 时切换到 cctv18 common 固定 commit 的工作流代码。
- 当前仍使用官方 manifest/common。
- extend 的正确实现尚未完成。
- 工作流仍有两处待重构：
  1. 复杂的 SysV KABI `sed` 逻辑；
  2. 运行时下载 EVDI 补丁的逻辑。
- `BUILD_FIX_SUMMARY.md` 是已有记录，保留不改。

## 已知验证结果

- 官方 common + 本仓库 standard：已知可启动。
- 平板 Pro extend：编译成功，但实际刷入后卡第一屏/黑屏。
- 一加 13 extend：编译成功，但尚未刷入测试。（主力机，并且有额外风驰逻辑，需要更谨慎对待）
- EVDI 是黑屏的重点排查对象。

## 下一步

1. 在官方 SM8650/SM8750 common 上检查并重做 standard 的静态 KABI 补丁。
2. 从 cctv18 项目提取 EVDI 代码，但针对官方 common 重新生成、检查并纳入本仓库的 KMI 版本化补丁。
3. extend 只应用 EVDI 补丁和三项配置：
   - `CONFIG_DRM_LINDROID_EVDI=y`
   - `CONFIG_BT_HCIVHCI`；
   - `CONFIG_STATIC_USERMODEHELPER=n`
4. 让补丁失败严格终止，不再使用远程可变补丁或 `|| true`。
5. 先做 `git apply --check`、配置核对、Kleaf/helper 测试和编译；不要未经必要修改就再次进行完整 40 分钟基线构建。

## 禁止回退

- 不恢复 common fork/固定 commit；
- 不继续堆叠 KABI `grep`/`sed` 分支；
