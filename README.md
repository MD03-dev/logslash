<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white" alt="C"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/github/stars/MD03-dev/logslash?style=for-the-badge&color=blue" alt="Stars"/>
</p>

<h1 align="center">⚡ logslash</h1>

<p align="center">
  <b>CLI tool lọc và phân tích log hỗn hợp — JSON, syslog, plain text</b><br>
  Chạy mượt mà trên Termux, không dependency nặng, tăng tốc bằng lõi C.
</p>

---

#### ✨ Tính năng nổi bật
- 🚀 **Tự động nhận diện:** Nhận biết JSON, syslog, plain text không cần cấu hình.
- 🧩 **Hỗ trợ Regex:** Thêm pattern cho các định dạng log lạ (Nginx, Apache...).
- 🎯 **Bộ lọc mạnh mẽ:** Lọc theo level, level-min, source, contains, since, until.
- 📊 **5 định dạng xuất:** json, ndjson, table (có màu), csv, pretty.
- ⚡ **Lõi C tăng tốc:** Detect nhanh gấp 4-10x so với Python thuần.
- 📱 **Tối ưu cho Termux:** Nhẹ, không cài đặt thư viện rườm rà.

---

#### 🚀 Hướng dẫn cài đặt (Termux)
1. Cài môi trường: `pkg install python clang make git -y`
2. Tải code: `git clone https://github.com/MD03-dev/logslash.git`
3. Cài đặt: `bash scripts/setup.sh`

#### 💻 Hướng dẫn sử dụng
- Xem định dạng: `logslash detect tests/sample.log`
- Lọc lỗi ra bảng: `logslash filter tests/sample3.log --level error -o table`
- Lọc từ mức Warn ra CSV: `logslash filter tests/sample3.log --level-min warn -o csv > report.csv`

---

#### 🤝 Đóng góp & License
Mọi đóng góp đều được hoan nghênh! Hãy xem file [CONTRIBUTING.md](CONTRIBUTING.md).
Nếu thấy dự án hữu ích, hãy tặng một ⭐ (Star) nhé!
Dự án phân phối dưới giấy phép **MIT**.

## 🔥 Tính năng nâng cao (Dành cho dân Hệ thống)
- **Hỗ trợ Pipe/Stdin:** Đọc log trực tiếp từ luồng, không cần lưu ra file. Ví dụ: `tail -f /var/log/syslog | logslash filter - --level error`
- **Tự động chống Crash:** Tự động bỏ qua các dòng log bị lỗi/hỏng (ví dụ JSON thiếu ngoặc) mà không làm gián đoạn tool.
- **Tự động tắt màu:** Nhận biết khi nào xuất ra file (pipe) để tự động tắt màu sắc, giúp file text sạch sẽ.
