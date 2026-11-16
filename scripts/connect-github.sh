#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export GIT_TERMINAL_PROMPT=0
mode=${1:---check}
if [[ "$mode" != '--check' && "$mode" != '--push' ]]; then
  printf '%s\n' '用法：bash scripts/connect-github.sh [--check|--push]' >&2
  exit 2
fi
if ! git remote get-url github >/dev/null 2>&1; then
  printf '%s\n' '尚未配置github远端。请先核对已有仓库并添加远端；本脚本不会另建仓库或覆盖成果。' >&2
  exit 2
fi
remote_url=$(git remote get-url github)
if [[ "$remote_url" != https://github.com/* ]]; then
  printf '%s\n' 'github远端不是预期的GitHub HTTPS地址，请核对后再运行。' >&2
  exit 2
fi
if [[ -n "$(git status --porcelain)" ]]; then
  printf '%s\n' '工作区有未提交修改，请先完成构建检查并提交，再核验/推送。' >&2
  exit 3
fi
git fetch github main
if ! git merge-base --is-ancestor github/main HEAD; then
  printf '%s\n' '远端有尚未合入的成果。请先核对并合并；不会强推或覆盖。' >&2
  exit 3
fi
if ! git push --dry-run github HEAD:refs/heads/main; then
  printf '%s\n' 'GitHub推送验证未通过。公开读取不等于写入授权。' '请通过Codex仓库/云环境设置为本项目完成GitHub授权，或在你自己的终端完成gh auth login --web。' '不要在聊天或仓库中发送密码、验证码或令牌。' >&2
  exit 2
fi
if [[ "$mode" == '--check' ]]; then
  printf '%s\n' '远端历史与推送dry-run通过；没有实际推送。要推送请加--push。'
  exit 0
fi
git push github HEAD:refs/heads/main
local_sha=$(git rev-parse HEAD)
remote_sha=$(git ls-remote github refs/heads/main | cut -f1)
if [[ "$local_sha" != "$remote_sha" ]]; then
  printf '%s\n' '推送后远端SHA不一致，请核查。' >&2
  exit 4
fi
printf '%s\n' "已推送：$remote_url" "提交：$local_sha" '请在仓库 Settings → Pages → Source 选择 GitHub Actions。Pages和原Sites是不同部署目标。'
