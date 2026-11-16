# 抽水蓄能电站：研究与网站开发

以中国抽水蓄能电站经济效益与效率问题为主题，以**辽宁清原一期6×300 MW**为案例。保留已有网站、历史容量电价样本与教学计算器。原站：https://qingyuan-hydro-thesis.aquaticbench3.chatgpt.site 。

## 当前可用范围

研究数据、来源、任务与网页放在同一个Git仓库。`research/data/` 是内容依据，`site/` 是网页模板，`scripts/build.py` 把数据与进度生成到 `dist/`，同时更新下载包。修改研究成果后执行构建与校验，网页及下载文件同步更新。只修改聊天内容或另一个ChatGPT项目不会自动修改仓库。

原站的Sites Git历史与现有GitHub初始提交均已保留。公开仓库：[Strategies-for-Improving-the-Economic-Efficiency-and-Performance-of-Pumped-Storage-Power-Stations](https://github.com/Yan888-clo/Strategies-for-Improving-the-Economic-Efficiency-and-Performance-of-Pumped-Storage-Power-Stations)。GitHub授权、源码与研究资料推送已完成，远端SHA已核对。main更新会触发GitHub Actions构建与检查。

GitHub Pages首次开通尚受限：当前连接修改Pages设置时返回403，需仓库所有者打开[Pages设置](https://github.com/Yan888-clo/Strategies-for-Improving-the-Economic-Efficiency-and-Performance-of-Pumped-Storage-Power-Stations/settings/pages)，在Source选择GitHub Actions，再重新运行工作流。工作流会在Pages未准备好时明确提示并跳过发布，不把检查通过当作已部署。**GitHub Pages与原Sites是两个独立部署目标，Pages成功不代表Sites自动更新。**

## 本地运行

需要 Python 3.10+；校验JavaScript需要Node.js。无npm依赖。

```sh
python scripts/build.py
python scripts/check.py
python -m http.server 8000 --directory dist
```

打开 `http://localhost:8000`。直接托管 `dist/`，不要托管整个仓库。原始下载包说明保留于 [docs/UPSTREAM_README.md](docs/UPSTREAM_README.md)。

## 目录

| 路径 | 用途 |
| --- | --- |
| `site/` | HTML/CSS/JS模板，保留已有交互与视觉 |
| `research/data/` | 清原参数JSON、同版CSV、96点统一结算点代理电价、2023容量电价样本 |
| `research/evidence/` | 原始公开电价响应、各方向检索记录、大陆HTTP探测原始记录 |
| `research/progress.json` | 任务、数据缺口、证据和发布状态 |
| `research/RESEARCH_PLAN.md` | 五个方向的计算路线与验收条件 |
| `research/CHANGELOG.md` | 研究与开发更新记录 |
| `docs/import-audit.json` | 源码导入来源、原始文件哈希与冲突核对 |
| `docs/DEPLOYMENT.md` | 原Sites发布、GitHub连接、自动部署及托管方案 |
| `docs/SYNC.md` | 同步范围与后续操作流程 |
| `dist/` | 构建后的公开网站与下载文件 |

## 每次研究更新

1. 新证据记录原始URL、日期、定位、数据性质及限制；按 [docs/DATA_POLICY.md](docs/DATA_POLICY.md)区分设计、代理、推导、假设、模型试验和现场实测。
2. 修改 `research/data/qingyuan_public_parameters.json`；同一价格快照的JSON与CSV成组更新。保留既有来源ID，缺口只有取得证据后才关闭。
3. 更新 `research/progress.json` 与 `research/CHANGELOG.md`。不把正在实施或受阻任务写成已完成。
4. 构建、校验、查看网页；提交研究数据、模板和生成结果的同一版本。
5. 按目标部署。GitHub Pages在连接完成后由main推送触发；原Sites需通过本项目的Sites发布操作完成，记录部署回执。

## 模型边界

现有水力功率与单位电量贡献计算器为教学情景，没有真实机组效率曲面、全站水量水头时序耦合、六机组合优化和实际结算单。负电价允许作为情景输入。3.78%结算线损率不能当作电站物理损失；统一结算点价格不是清原节点价格。完整库容曲线、效率曲面、运行记录等16组缺口继续保留。

## 授权与公开范围

[LICENSE](LICENSE)的MIT许可仅覆盖原创HTML/CSS/JavaScript；第三方数据、来源网站、论文与商标遵从原权利。新增Python与Shell脚本也以MIT提供，保留原代码许可范围说明。公开仓库与下载包只保留结构化数据及来源记录，不包含第三方论文全文或账号凭据。不要提交`.env`、访问令牌、个人账号配置或原始站点访问名单。

国内可访问性报告在 `research/evidence/hosting_reachability.json`：2026-11-16的大陆三运营商探针访问首页、研究页、ZIP均HTTP403；当前云机匿名访问成功。不能据此声称大陆已正常可用，也不能把该探测直接推广为所有普通浏览器不可访问。
