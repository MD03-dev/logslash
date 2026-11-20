# logstash

> **CLI tool lọc phân thích log hỗn hợp — JSON, syslog, plain text — chạy mượt trên Termux, không dependency nặng.**
`logslash` sinh ra từ một vấn đề rất cụ thể: log ở đâu cũng có, nhưng mỗi service một format, lỗi tool một kiồu filter.
`logslash` gom tất cả về nhối: **detect → parse → filter → output**, cức này chạy mượt trên điện thoại.

### 🤟 Tính năng
- Tự động nhận diện format (JSON, syslog, plain)
- Cấu hình Regex tùy chỉnh
- Bộ lọc mạnh
- Dăng xuất 5 file: Json, Ndjson, Table, CSV, Pretty
- Môle C tĠng tốc 4-10x, cực nhanh cức nhanh.

### 🚀 Cài đặt (Nhanh.)
```bash
pkg install python clang make git
bash scripts/setup.sh
```

### 💻 Hướng dẫn sử dụng
```bash
logslash detect tests/sample.log
logslash filter tests/sample3.log --level error -o table
```

### 🔓 License
MIT
