#!/bin/zsh
set -e
cd -- "$(dirname -- "$0")"
if [[ -x .venv/bin/python ]]; then
  VIBE_PYTHON="$PWD/.venv/bin/python"
elif [[ -x ../../work/venv/bin/python ]]; then
  VIBE_PYTHON="$PWD/../../work/venv/bin/python"
else
  print '请先按 README.md 安装项目依赖。'
  read '?按回车关闭'
  exit 1
fi
print '在浏览器打开 http://127.0.0.1:8765 ，按 Ctrl+C 停止预览。'
"$VIBE_PYTHON" studio.py preview projects/frame-story --port 8765
