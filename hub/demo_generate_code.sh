#!/bin/bash
# Demo script: Tạo mã kích hoạt nhanh cho testing

set -e

echo "🚀 CareVL Hub - Demo tạo mã kích hoạt"
echo "======================================"
echo ""

# Thông tin demo (thay bằng thông tin thật khi deploy)
STATION_ID="TRAM_DEMO_001"
STATION_NAME="Trạm Y Tế Demo"
REPO_URL="https://github.com/carevl-bot/station-demo-001"
PAT="ghp_demo_token_replace_with_real_pat"

echo "📋 Thông tin trạm:"
echo "  - Station ID: $STATION_ID"
echo "  - Station Name: $STATION_NAME"
echo "  - Repo URL: $REPO_URL"
echo "  - PAT: ${PAT:0:10}... (hidden)"
echo ""

echo "🔧 Tạo mã kích hoạt..."
echo ""

# Tạo mã
uv run carevl-hub admin generate-code \
  --station-id "$STATION_ID" \
  --station-name "$STATION_NAME" \
  --repo-url "$REPO_URL" \
  --pat "$PAT"

echo ""
echo "✅ Xong! Copy mã ở trên và dán vào Edge app tại /provision/"
echo ""
echo "💡 Tip: Để tạo nhiều mã cùng lúc, dùng:"
echo "   uv run carevl-hub admin create-csv-template"
echo "   uv run carevl-hub admin generate-batch --input-csv stations.csv"
