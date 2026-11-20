#!/data/data/com.termux/files/usr/bin/bash
# Compile module C tăng tốc.
# Chạy: bash scripts/build_c.sh

set -e
cd "$(dirname "$0")/.."

echo "=== Build C module ==="

if ! command -v gcc >/dev/null 2>&1; then
    echo "⚠️  gcc không có sẵn."
    echo "   Termux: pkg install clang"
    echo "   (module C là optional, logslash vẫn chạy bằng Python thuần)"
    exit 1
fi

SRC="logslash/cdetect.c"
OUT="logslash/libcdetect.so"

if [ ! -f "$SRC" ]; then
    echo "❌ Không tìm thấy $SRC"
    exit 1
fi

echo "Compile: $SRC -> $OUT"
gcc -O2 -shared -fPIC -o "$OUT" "$SRC"

if [ -f "$OUT" ]; then
    SIZE=$(stat -c%s "$OUT" 2>/dev/null || stat -f%z "$OUT" 2>/dev/null || echo "?")
    echo "✅ Build thành công: $OUT (${SIZE} bytes)"
else
    echo "❌ Build thất bại"
    exit 1
fi
