# 部署、账号连接与访问验证

## 原Sites站点

站点ID：`appgprj_6afa7f3df0048191a958ae780f2c34c8`。地址：https://qingyuan-hydro-thesis.aquaticbench3.chatgpt.site 。本会话已验证当前账号owner权限，access_mode为public。保留`.openai/hosting.json`的同一ID；不创建新站。

辅助命令：`python scripts/prepare-sites-release.py`从隐藏stdin接收本次Sites短效凭据JSON，构建检查、核对远端历史、提交/推送并输出归档与提交SHA；它本身不会调用发布API。

正常流程：运行build/check → 推送同一提交至Sites源仓库main → 用Sites保存该提交与含`.openai/hosting.json`及`dist/`的部署归档 → 对保存的版本发布 → 查看成功回执 → 匿名核对首页、研究页、数据和下载。每个发布URL都是正式环境。

本环境没有技能文档所述的`site-workflow.mjs`，因此采用等价的标准Git推送与本地归档，凭据仅从隐藏stdin传入进程内存，不写入源码或Git配置。发布仍使用原生Sites工具核验提交和保存版本。Sites短效仓库凭据不能放进GitHub Actions冒充长期同步配置。

## GitHub：当前受阻步骤

初始工作区没有用户Git仓库，原站仅关联Sites托管Git；`gh auth status`报告现有GH_TOKEN无效，GitHub插件未连接。已展示GitHub连接入口，但后台没有确认完成可用授权。

用户需要完成：

1. 在ChatGPT设置的插件/连接器中连接或重新连接GitHub，完成GitHub账号授权，允许访问目标仓库；如需组织仓库，还要完成组织SSO/仓库授权。
2. 让当前环境使用有效GitHub连接。在自己的终端也可通过`gh auth login --web`完成授权；不要把token粘进公开仓库。
3. 授权可用后在项目执行 `bash scripts/connect-github.sh`。脚本优先检查`github`远端；发现同名仓库会停止以便核对，不强推。不存在时按用户指示创建公开`qingyuan-hydro-thesis`仓库，保留原Sites origin。
4. 在GitHub仓库Settings → Pages → Build and deployment → Source选择GitHub Actions，运行`.github/workflows/pages.yml`。

工作流在main更新后执行build/check并发布`dist/`，不需要访客登录；PR只检查不部署。不包含Sites发布凭据，也不会修改原Sites。公开仓库地址与Pages URL应在创建和成功部署后写入progress的sync字段；当前不得预填一个虚构用户URL。

## 中国大陆实际探测

2026-11-16约04:36—04:38 UTC，Globalping中国大陆测试点：桂林电信AS4134、武汉联通AS4837、台山移动AS9808。首页、研究页、源码ZIP共9次HTTPS GET均TLS验证通过但HTTP403，返回Cloudflare安全阻断，不是登录要求。当前云机匿名GET为200。原始结果和测量ID见`research/evidence/hosting_reachability.json`及`globalping-*-results.json`。

该结果仅证明这些测试请求当时被拦，不能保证所有浏览器不可用。尚无“国内已正常访问”的验证结论。需要在大陆普通浏览器（无登录、无代理）分别验证首页、研究页、参数CSV、ZIP下载，并记录时间、运营商、城市、HTTP结果和截图。部署镜像后须重复测试。

## 可执行备选与费用（未采购）

| 方案 | 配置与账号 | 费用边界 | 大陆可达性 |
| --- | --- | --- | --- |
| 保留原Sites | 已有owner权限、公网站点 | 本次没有新增主机或域名采购；账号套餐以平台账单为准 | 三运营商探针403；平台防护不能由静态源码解除 |
| GitHub Pages镜像 | 公开GitHub仓库＋本仓库Actions＋启用Pages | GitHub Free公开仓库基础托管0元；自定义域名另计 | 部署后再测，不能保证 |
| Cloudflare Pages镜像 | 用户Cloudflare账号连接GitHub，构建`python scripts/build.py`，输出`dist` | Pages Free基础静态托管0元，500构建/月；超配额按官方规则；域名另计 | 同属Cloudflare生态，须另测，不能保证解除阻断 |
| 阿里云OSS中国大陆地域 | 用户阿里云账号、Bucket静态网站、自定义域名、ICP备案；CI凭据只配置仓库Secrets | 存储GB月＋请求次数＋公网流量，域名按注册/续费报价；未选地域/流量无法给固定月费 | 适合做大陆镜像，需部署后实测 |
| 腾讯云COS中国大陆地域 | 用户腾讯云账号、Bucket静态网站、自定义域名及相关备案，CI密钥置Secrets | 按地域存储、请求、流量及域名计费；未选用量不虚构总价 | 同上，需实测 |

官方依据：[GitHub Pages限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)、[Cloudflare Pages限制](https://developers.cloudflare.com/pages/platform/limits/)、[OSS静态网站](https://help.aliyun.com/zh/oss/user-guide/hosting-static-websites)、[OSS价格](https://www.aliyun.com/price/detail/oss)、[COS价格](https://cloud.tencent.com/product/cos/pricing)。动态价格页与历史示例不同，购买时需确认地域、预期存储/下载流量、备案主体、域名注册/续费价格后再预算。本次未注册域名、未开通付费云资源。
