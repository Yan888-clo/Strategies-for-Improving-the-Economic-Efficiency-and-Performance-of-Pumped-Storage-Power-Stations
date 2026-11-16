#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! gh api user --jq .login >/dev/null 2>&1; then
  printf '%s\n' 'GitHub尚未授权。请先在ChatGPT设置→插件→GitHub完成连接，并重新运行本脚本。' '也可在你自己的终端运行 gh auth login --web；不要把令牌写入仓库。' >&2
  exit 2
fi
if git remote get-url github >/dev/null 2>&1; then
  gh repo view "$(git remote get-url github)" --json url,isPrivate
  printf '%s\n' '已存在github远端。请先核对远端历史；本脚本不会覆盖或强制推送。'
  exit 0
fi
owner=$(gh api user --jq .login)
repo_name=${1:-qingyuan-hydro-thesis}
if gh repo view "$owner/$repo_name" --json url >/dev/null 2>&1; then
  printf '%s\n' "发现现有仓库 $owner/$repo_name。请先git fetch核对内容，再设置github远端；本脚本不覆盖现有仓库。"
  exit 3
fi
# User requested a public repository. Existing Sites origin is preserved.
gh repo create "$owner/$repo_name" --public --source=. --remote=github --push --description '辽宁清原一期6×300MW：抽水蓄能经济性、效率与研究网站'
printf '%s\n' "仓库：https://github.com/$owner/$repo_name" '请在仓库 Settings → Pages → Source 选择 GitHub Actions。工作流将在main更新后构建和发布。'
