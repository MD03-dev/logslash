# logslash

> CLI tool phân tích log hỗn hợp — JSON, syslog, plain text.

## Tính năng
- Tự detect format (JSON, syslog, plain)
- Custom regex parser
- Filter linh hoạt (level, source, contains...)
- 5 output formats (json, ndjson, table, csv, pretty)
- Module C tăng tốc 4-10x
- Chạy tốt trên Termux

## Cài đặt
```bash
pkg install python clang make
git clone https://github.com/TEN_BAN/logslash.git
cd logslash
bash scripts/setup.sh
```

## Cách dùng
```bash
logslash detect tests/sample.log
logslash filter tests/sample3.log --level error -o table
```

## License
MIT
