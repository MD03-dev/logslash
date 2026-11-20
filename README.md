logslash

CLI tool lọc và phân tích log hỗn hợp — JSON, syslog, plain text — chạy mượt mà trên Termux, không dependency nặng.

logslash sinh ra từ một vấn đề rất cụ thể: log ở đâu cũng có, nhưng mỗi service một format. grep thì không hiểu JSON, jq thì không hiểu syslog, awk thì không ai nhớ nổi cú pháp. logslash gom tất cả về một mối: detect → parse → filter → output, tất cả trong một lệnh duy nhất.

✨ Tính năng nổi bật

· Tự động nhận diện: Tự nhận biết JSON, syslog RFC 3164, plain text mà không cần cấu hình.
· Hỗ trợ Regex tùy chỉnh: Dễ dàng thêm pattern cho các định dạng log lạ (Nginx, Apache...).
· Bộ lọc mạnh mẽ: Lọc theo level, level-min, source, contains, not-contains, since, until.
· 5 định dạng xuất: json, ndjson, table (có màu), csv, pretty.
· Lõi C tăng tốc: Tốc độ detect nhanh gấp 4-10x (tự động fallback về Python nếu máy không có C compiler).
· Tối ưu cho Termux: Nhẹ, không cài đặt thư viện rườm rà.

---

🚀 Hướng dẫn cài đặt (Dành cho người mới)

Bước 1: Cài đặt môi trường
Mở Termux lên và chạy lệnh sau để cài Python và trình biên dịch C:
pkg update && pkg upgrade -y
pkg install python clang make git -y

Bước 2: Tải source code về máy
git clone https://github.com/MD03-dev/logslash.git
cd logslash

Bước 3: Setup và Build tự động
Chạy script này để hệ thống tự động cài đặt, build module C và chạy test thử:
bash scripts/setup.sh

Bước 4: Cài đặt thành lệnh toàn cục
Để có thể gõ lệnh logslash ở bất kỳ thư mục nào, bạn chạy:
bash scripts/install.sh

---

💻 Hướng dẫn sử dụng (Từ A đến Z)

1. Xem file log thuộc định dạng nào?
logslash detect tests/sample.log

2. Chuyển log thành JSON
logslash parse tests/sample3.log --limit 2

3. Lọc lỗi và xuất ra bảng
logslash filter tests/sample3.log --level error -o table

4. Lọc từ mức Warn trở lên, xuất ra file CSV
logslash filter tests/sample3.log --level-min warn -o csv > report.csv

5. Dùng Regex tùy chỉnh cho log Nginx
logslash parse tests/sample2.log --patterns tests/patterns.json -o table

---

🏎️ Hiệu năng (Benchmark)

Chạy lệnh sau để thấy tốc độ tăng vọt:
make bench
(Kết quả thực tế: Tăng tốc 4.2x so với Python thuần).

---

🤝 Đóng góp (Contributing)

Mọi đóng góp đều được hoan nghênh! Hãy xem file CONTRIBUTING.md để biết chi tiết. Nếu bạn thấy dự án hữu ích, hãy tặng một ⭐ (Star) để ủng hộ tác giả nhé!

📄 License

Dự án được phân phối dưới giấy phép MIT. Xem file LICENSE để biết thêm.
