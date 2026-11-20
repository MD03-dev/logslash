#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "=== TEST LOGSLASH ==="
echo "Thư mục: $(pwd)"
echo

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    local expect="$3"
    echo "--- Test: $name"
    output=$(eval "$cmd" 2>&1) || true
    if echo "$output" | grep -q "$expect"; then
        echo "  ✅ PASS"
        PASS=$((PASS + 1))
    else
        echo "  ❌ FAIL"
        echo "  Lệnh: $cmd"
        echo "  Kỳ vọng chứa: $expect"
        echo "  Thực tế:"
        echo "$output" | sed 's/^/    /'
        FAIL=$((FAIL + 1))
    fi
    echo
}

# ===== Phần 1 =====
check "import logslash" \
    "python -c 'import logslash; print(logslash.__version__)'" "0.1.0"
check "detect json" \
    "python -c 'from logslash.detector import detect_format; print(detect_format(\"{\\\"a\\\":1}\"))'" "json"
check "detect syslog" \
    "python -c 'from logslash.detector import detect_format; print(detect_format(\"Jan  5 12:00:00 host app[1]: hi\"))'" "syslog"
check "detect plain" \
    "python -c 'from logslash.detector import detect_format; print(detect_format(\"hello world\"))'" "plain"
check "cli version" "python -m logslash version" "v0.1.0"
check "cli detect file" "python -m logslash detect tests/sample.log" "Format chủ đạo: json"
check "cli detect file không tồn tại" \
    "python -m logslash detect /tmp/khong_ton_tai.log" "không tìm thấy file"

# ===== Phần 2 =====
check "parse_json level" \
    "python -c 'from logslash.parsers.json_parser import parse_json; print(parse_json(\"{\\\"level\\\":\\\"info\\\",\\\"msg\\\":\\\"ok\\\"}\")[\"level\"])'" "info"
check "parse_json message" \
    "python -c 'from logslash.parsers.json_parser import parse_json; print(parse_json(\"{\\\"level\\\":\\\"info\\\",\\\"msg\\\":\\\"ok\\\"}\")[\"message\"])'" "ok"
check "parse_json extra" \
    "python -c 'from logslash.parsers.json_parser import parse_json; r=parse_json(\"{\\\"msg\\\":\\\"x\\\",\\\"port\\\":8080}\"); print(r[\"extra\"][\"port\"])'" "8080"
check "parse_json invalid trả None" \
    "python -c 'from logslash.parsers.json_parser import parse_json; print(parse_json(\"not json\") is None)'" "True"
check "parse_plain bracket level" \
    "python -c 'from logslash.parsers.plain_parser import parse_plain; print(parse_plain(\"[INFO] server started\")[\"level\"])'" "info"
check "parse_plain prefix level" \
    "python -c 'from logslash.parsers.plain_parser import parse_plain; print(parse_plain(\"ERROR: boom\")[\"level\"])'" "error"
check "parse_plain timestamp" \
    "python -c 'from logslash.parsers.plain_parser import parse_plain; print(parse_plain(\"2025-01-05T12:00:00Z hello\")[\"timestamp\"])'" "2025-01-05T12:00:00Z"
check "normalize warning" \
    "python -c 'from logslash.parsers.base import normalize_level; print(normalize_level(\"WARNING\"))'" "warn"
check "cli parse ndjson" "python -m logslash parse tests/sample.log --ndjson --limit 1" "server started"
check "cli parse full" "python -m logslash parse tests/sample.log" "connection refused"

# ===== Phần 3 =====
check "parse_syslog source" \
    "python -c 'from logslash.parsers.syslog_parser import parse_syslog; r=parse_syslog(\"Jan  5 12:00:00 myhost sshd[1234]: hi\"); print(r[\"source\"])'" "myhost"
check "parse_syslog message" \
    "python -c 'from logslash.parsers.syslog_parser import parse_syslog; r=parse_syslog(\"Jan  5 12:00:00 myhost sshd[1234]: hi\"); print(r[\"message\"])'" "hi"
check "parse_syslog pid" \
    "python -c 'from logslash.parsers.syslog_parser import parse_syslog; r=parse_syslog(\"Jan  5 12:00:00 myhost sshd[1234]: hi\"); print(r[\"extra\"][\"pid\"])'" "1234"
check "parse_syslog invalid trả None" \
    "python -c 'from logslash.parsers.syslog_parser import parse_syslog; print(parse_syslog(\"not syslog\") is None)'" "True"
check "regex parser match" \
    "python -c 'from logslash.parsers.regex_parser import RegexParser; rp=RegexParser([{\"name\":\"t\",\"regex\":\"^(?P<level>[A-Z]+) \\\\| (?P<message>.*)\$\"}]); r=rp.parse(\"INFO | hello\"); print(r[\"level\"])'" "info"
check "cli parse sample2 có regex" \
    "python -m logslash parse tests/sample2.log --ndjson --patterns tests/patterns.json" "regex:nginx_access"

# ===== Phần 4: filter =====
check "filter level error" \
    "python -m logslash filter tests/sample3.log --ndjson --level error" "connection timeout"
check "filter level error chỉ 2 record" \
    "python -m logslash filter tests/sample3.log --ndjson --level error --stats 2>&1 | grep -c '2 record'" "1"
check "filter level_min warn" \
    "python -m logslash filter tests/sample3.log --ndjson --level-min warn" "slow query"
check "filter level_min warn không có info" \
    "python -m logslash filter tests/sample3.log --ndjson --level-min warn | grep -c 'server started'" "0"
check "filter source api" \
    "python -m logslash filter tests/sample3.log --ndjson --source api" "request ok"
check "filter contains timeout" \
    "python -m logslash filter tests/sample3.log --ndjson --contains timeout" "timeout reading config"
check "filter not_contains timeout" \
    "python -m logslash filter tests/sample3.log --ndjson --not-contains timeout | grep -c 'timeout'" "0"
check "filter since" \
    "python -m logslash filter tests/sample3.log --ndjson --since 2025-01-05T12:00:20Z" "cache hit"
check "filter until" \
    "python -m logslash filter tests/sample3.log --ndjson --until 2025-01-05T12:00:10Z" "slow query"
check "filter format json" \
    "python -m logslash filter tests/sample3.log --ndjson --format json --limit 1" "server started"
check "filter kết hợp level+contains" \
    "python -m logslash filter tests/sample3.log --ndjson --level error --contains config" "timeout reading config"
check "filter show_filter" \
    "python -m logslash filter tests/sample3.log --ndjson --level error --show-filter 2>&1 | grep 'level=error'" "level=error"
check "filter level_min invalid" \
    "python -m logslash filter tests/sample3.log --level-min xxx 2>&1" "không hợp lệ"

# ===== Phần 5: output formats =====
check "output table có header" \
    "python -m logslash parse tests/sample3.log -o table --limit 2" "TIMESTAMP"
check "output table có dữ liệu" \
    "python -m logslash parse tests/sample3.log -o table" "server started"
check "output csv có header" \
    "python -m logslash parse tests/sample3.log -o csv --limit 1" "timestamp,level,source"
check "output csv có message" \
    "python -m logslash parse tests/sample3.log -o csv" "connection timeout"
check "output json vẫn hoạt động" \
    "python -m logslash parse tests/sample3.log -o json --limit 1" "\"level\": \"info\""
check "output pretty" \
    "python -m logslash parse tests/sample3.log -o pretty --limit 1" "server started"
check "output ndjson vẫn hoạt động" \
    "python -m logslash parse tests/sample3.log -o ndjson --limit 1" "server started"
check "flag --ndjson cũ vẫn chạy" \
    "python -m logslash parse tests/sample3.log --ndjson --limit 1" "server started"
check "output sai trả lỗi argparse" \
    "python -m logslash parse tests/sample3.log -o xxx 2>&1" "invalid choice"
check "filter + table" \
    "python -m logslash filter tests/sample3.log --level error -o table" "connection timeout"
check "filter + csv" \
    "python -m logslash filter tests/sample3.log --level error -o csv" "timeout reading config"

check "pretty output là JSON hợp lệ" \
    "python -m logslash parse tests/sample3.log -o pretty --limit 1 | python -c 'import json,sys; json.load(sys.stdin); print(\"VALID\")'" "VALID"

# ===== Phần 6: C module =====
check "cdetect py import" \
    "python -c 'from logslash import cdetect; print(\"ok\")'" "ok"
check "cdetect detect json khớp python" \
    "python -c 'from logslash.detector import detect_format; print(detect_format(\"{\\\"a\\\":1}\"))'" "json"
check "cdetect detect syslog khớp python" \
    "python -c 'from logslash.detector import detect_format; print(detect_format(\"Jan  5 12:00:00 host app[1]: hi\"))'" "syslog"
check "cdetect detect plain khớp python" \
    "python -c 'from logslash.detector import detect_format; print(detect_format(\"hello world\"))'" "plain"
check "bench chạy được" \
    "python -m logslash bench tests/sample3.log --repeat 10" "Python thuần"
check "bench có tăng tốc" \
    "python -m logslash bench tests/sample3.log --repeat 10 2>&1 | grep -c 'Tăng tốc'" "1"

echo "================================"
echo "KẾT QUẢ: $PASS PASS, $FAIL FAIL"
echo "================================"
if [ "$FAIL" -gt 0 ]; then exit 1; fi
exit 0
