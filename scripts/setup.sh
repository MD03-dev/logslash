#!/data/data/com.termux/files/usr/bin/bash
# Setup logslash trên Termux.
# Chạy: bash scripts/setup.sh

set -e
cd "$(dirname "$0")/.."

echo "=== SETUP LOGSLASH ==="
echo "Thư mục: $(pwd)"
echo

# 1. Kiểm tra Python
if ! command -v python >/dev/null 2>&1; then
    echo "📦 Cài Python..."
    pkg install -y python
else
    echo "✅ Python: $(python --version 2>&1)"
fi

# 2. Kiểm tra gcc/clang (optional, cho C module)
if command -v gcc >/dev/null 2>&1; then
    echo "✅ gcc: $(gcc --version | head -1)"
    echo "🔨 Build C module..."
    bash scripts/build_c.sh || echo "⚠️  Build C thất bại, dùng Python thuần"
elif command -v clang >/dev/null 2>&1; then
    echo "✅ clang: $(clang --version | head -1)"
    echo "🔨 Build C module..."
    bash scripts/build_c.sh || echo "⚠️  Build C thất bại, dùng Python thuần"
else
    echo "⚠️  Không có gcc/clang. Module C sẽ không build."
    echo "   Cài: pkg install clang"
fi

echo
echo "=== CHẠY TEST ==="
bash scripts/test_all.sh

echo
echo "=== HOÀN TẤT ==="
echo "Chạy thử:"
echo "  python -m logslash --help"
echo "  python -m logslash detect tests/sample.log"
echo "  python -m logslash filter tests/sample3.log --level error -o table"
echo
echo "Cài thành lệnh toàn cục:"
echo "  bash scripts/install.sh"
