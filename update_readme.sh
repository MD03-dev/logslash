#!/data/data/com.termux/files/usr/bin/bash

if [ -z "$1" ]; then
    echo "❌ Lỗi: Bạn chưa nhập Token!"
    echo "Cách dùng: bash update_readme.sh TOKEN_CUA_BAN"
    exit 1
fi

TOKEN="$1"

# 1. Lấy SHA hiện tại của file README trên GitHub
echo "Đang lấy mã SHA..."
SHA=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/repos/MD03-dev/logslash/contents/README.md | grep -o '"sha": "[^"]*"' | head -1 | cut -d '"' -f 4)

if [ -z "$SHA" ]; then
    echo "❌ Không lấy được mã SHA. Có thể Token sai hoặc Repo không tồn tại."
    exit 1
fi

# 2. Tạo nội dung README chuẩn (mã hóa Base64)
echo "Đang tạo nội dung..."
cat << 'MARKDOWN' > README_TEMP.md
### 🚀 logslash
**CLI tool lọc và phân tích log hỗn hợp — JSON, syslog, plain text — chạy mượt mà trên Termux.**

`logslash` sinh ra từ một vấn đề rất cụ thể: log ở đâu cũng có, nhưng mỗi service một format. `grep` thì không hiểu JSON, `jq` thì không hiểu syslog. `logslash` gom tất cả về một mối: **detect → parse → filter → output**, tất cả trong một lệnh duy nhất.

#### ✨ Tính năng nổi bật
* **Tự động nhận diện:** Nhận biết JSON, syslog, plain text không cần cấu hình.
* **Hỗ trợ Regex:** Thêm pattern cho các định dạng log lạ (Nginx, Apache...).
* **Bộ lọc mạnh mẽ:** Lọc theo level, level-min, source, contains, since, until.
* **5 định dạng xuất:** json, ndjson, table (có màu), csv, pretty.
* **Lõi C tăng tốc:** Detect nhanh gấp 4-10x so với Python thuần.
* **Tối ưu cho Termux:** Nhẹ, không cài đặt thư viện rườm rà.

---

#### 🚀 Hướng dẫn cài đặt (Termux)

**1. Cài đặt môi trường:**
`pkg update && pkg upgrade -y`
`pkg install python clang make git -y`

**2. Tải source code:**
`git clone https://github.com/MD03-dev/logslash.git`
`cd logslash`

**3. Build và cài đặt:**
`bash scripts/setup.sh`
`bash scripts/install.sh`

---

#### 💻 Hướng dẫn sử dụng

**Xem file log thuộc định dạng nào:**
`logslash detect tests/sample.log`

**Lọc lỗi và xuất ra bảng màu:**
`logslash filter tests/sample3.log --level error -o table`

**Lọc từ mức Warn trở lên, xuất CSV:**
`logslash filter tests/sample3.log --level-min warn -o csv > report.csv`

**Dùng Regex tùy chỉnh (Nginx):**
`logslash parse tests/sample2.log --patterns tests/patterns.json -o table`

---

#### 🤝 Đóng góp & License
Mọi đóng góp đều được hoan nghênh! Hãy xem file [CONTRIBUTING.md](CONTRIBUTING.md) để biết chi tiết.
Nếu bạn thấy dự án hữu ích, hãy tặng một ⭐ (Star) để ủng hộ tác giả nhé!

Dự án được phân phối dưới giấy phép **MIT**.
MARKDOWN

# 3. Mã hóa Base64 và xóa file tạm
BASE64_CONTENT=$(base64 -w 0 README_TEMP.md)
rm README_TEMP.md

# 4. Gửi API cập nhật lên GitHub
echo "Đang cập nhật lên GitHub..."
JSON_DATA="{\"message\": \"docs: cap nhat README cuc dep\", \"sha\": \"$SHA\", \"content\": \"$BASE64_CONTENT\"}"

RESPONSE=$(curl -s -X PUT -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/MD03-dev/logslash/contents/README.md -d "$JSON_DATA")

if echo "$RESPONSE" | grep -q '"commit"'; then
    echo "✅ THÀNH CÔNG RỰC RỠ! Bạn hãy F5 lại trang GitHub để xem kết quả."
else
    echo "❌ Có lỗi xảy ra:"
    echo "$RESPONSE"
fi
