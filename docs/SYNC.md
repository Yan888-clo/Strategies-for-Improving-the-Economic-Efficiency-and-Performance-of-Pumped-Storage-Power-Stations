# 同步范围与更新步骤

当前内容链为：`research/data + research/progress.json + site → scripts/build.py → dist网页/数据/源码ZIP → 同一Git提交 → 目标主机发布`。

已经具备的是同仓库与可复现构建；构建会生成参数表、来源索引、缺口、任务、价格图数据和下载包。`research/sources/index.json`如存在属于生成副本，以参数JSON的`sources`为准。

以下边界不能省略：

- 另一个ChatGPT项目的聊天、文件上传或回答不会自动进入此仓库。把新成果整理进本仓库后才能进入构建链。
- 没有配置定时自动科研抓取；新增来源由研究者核实后提交。网页不会自行补造缺失参数。
- GitHub Pages工作流准备就绪，只有授权、仓库和Pages配置完成后才会在main提交后自动部署。
- 原Sites有独立源仓库与版本发布操作。GitHub Pages工作流不具备Sites的长效发布凭据，不自动更新原Sites。
- 原Sites更新由有权的后续Codex/Sites会话读取当前仓库、运行构建校验、推送Sites源分支、保存并发布同一提交。所有研究和源码变更随该版本一起更新。
- GitHub与Sites双远端时，保留`origin`为Sites，`github`为用户公开仓库。每次先fetch并核对两边历史，不强推、不覆盖远端新成果。

## 版本与回执

`dist/sync-manifest.json`提供本次构建输入哈希与输出信息。发布后保存Sites返回的version/deployment/commit/url回执到工作区的`local-status/`（已忽略），并在研究更新记录中保留发布日期与实际验证范围。

任何“已同步”“已公开”“国内可用”的状态分别需要构建检查、发布成功回执、匿名HTTP验证及大陆网络证据。不能仅凭生成文件或CI配置就宣称已部署。
