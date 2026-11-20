### 🚀 logslash

**CLI tool lọc và phân tích log hỗn hợp — JSON, syslog, plain text**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![C](https://img.shields.io/badge/C-00599C?style=flat-square&logo=c&logoColor=white)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/MD03-dev/logslash?style=flat-square&color=blue)](https://github.com/MD03-dev/logslash)

---

`logslash` sinh ra từ một vấn đề rất cụ thể: log ở đâu cũng có, nhưng mỗi service một format. `grep` thì không hiểu JSON, `jq` thì không hiểu syslog. `logslash` gom tất cả về một mối: **detect → parse → filter → output** trong một lệnh duy nhất.

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
