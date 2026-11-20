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
