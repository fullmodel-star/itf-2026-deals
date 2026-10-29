#!/usr/bin/env bash
# 用法: bash shot.sh <網址> <輸出png完整路徑> [高度,預設3000]
# 需以 dangerouslyDisableSandbox 執行（沙盒內 DNS 不通）
URL="$1"; OUT="$2"; H="${3:-3000}"
PROF="$TEMP/claude/itf_prof_$$"
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars \
  --user-data-dir="$PROF" --window-size=1280,"$H" --virtual-time-budget=10000 \
  --lang=zh-TW --screenshot="$OUT" "$URL" 2>&1 | grep -E "written|failed"
rm -rf "$PROF"
