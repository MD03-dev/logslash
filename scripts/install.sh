#!/data/data/com.termux/files/usr/bin/bash
# Cài logslash thành lệnh toàn cục trong $PREFIX/bin.
# Chạy: bash scripts/install.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$(pwd)"

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
BIN_DIR="$PREFIX/bin"

if [ ! -d "$BIN_DIR" ]; then
    echo "❌ Không tìm thấy $BIN_DIR"
    echo "   Biến PREFIX có thể chưa đúng. Chạy: echo \$PREFIX"
    exit 1
fi

LAUNCHER="$BIN_DIR/logslash"

echo "=== CÀI LOGSLASH ==="
echo "Root: $ROOT"
echo "Launcher: $LAUNCHER"
echo

cat > "$LAUNCHER" << LAUNCHER_EOF
#!/data/data/com.termux/files/usr/bin/bash
cd "$ROOT" && exec python -m logslash "\$@"
LAUNCHER_EOF

chmod +x "$LAUNCHER"

echo "✅ Đã cài. Chạy thử:"
echo "  logslash --help"
echo "  logslash detect tests/sample.log"
echo
echo "Gỡ cài đặt:"
echo "  rm $LAUNCHER"
