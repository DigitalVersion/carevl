#!/bin/bash
# Demo script: Tạo hàng loạt mã kích hoạt từ CSV

set -e

echo "🚀 CareVL Hub - Demo tạo hàng loạt mã kích hoạt"
echo "==============================================="
echo ""

# Tạo CSV demo
CSV_FILE="stations_demo.csv"
OUTPUT_DIR="./invite_codes_demo"

echo "📝 Tạo file CSV demo: $CSV_FILE"
cat > "$CSV_FILE" << 'EOF'
station_id,station_name,repo_url,pat,encryption_key
TRAM_001,Trạm Y Tế Xã A,https://github.com/carevl-bot/station-001,ghp_demo_token_001,
TRAM_002,Trạm Y Tế Xã B,https://github.com/carevl-bot/station-002,ghp_demo_token_002,
TRAM_003,Trạm Y Tế Xã C,https://github.com/carevl-bot/station-003,ghp_demo_token_003,
EOF

echo "✓ File CSV đã tạo"
echo ""

echo "📋 Nội dung CSV:"
cat "$CSV_FILE"
echo ""

echo "🔧 Tạo mã kích hoạt hàng loạt..."
echo ""

# Tạo hàng loạt
uv run carevl-hub admin generate-batch \
  --input-csv "$CSV_FILE" \
  --output-dir "$OUTPUT_DIR"

echo ""
echo "✅ Xong! Kiểm tra thư mục: $OUTPUT_DIR"
echo ""

# Hiển thị kết quả
if [ -d "$OUTPUT_DIR" ]; then
  echo "📂 Các file đã tạo:"
  ls -lh "$OUTPUT_DIR"
  echo ""
  
  echo "📄 Nội dung mã đầu tiên:"
  FIRST_FILE=$(ls "$OUTPUT_DIR" | head -n 1)
  if [ -n "$FIRST_FILE" ]; then
    cat "$OUTPUT_DIR/$FIRST_FILE"
  fi
fi

echo ""
echo "💡 Tip: Sửa file $CSV_FILE với thông tin thật, sau đó chạy lại script này"
echo "💡 Hoặc chạy trực tiếp:"
echo "   uv run carevl-hub admin generate-batch --input-csv $CSV_FILE --output-dir $OUTPUT_DIR"
