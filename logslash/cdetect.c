/*
 * cdetect.c - Module C tăng tốc detect format log.
 *
 * Compile:
 *   gcc -O2 -shared -fPIC -o logslash/libcdetect.so logslash/cdetect.c
 *
 * API:
 *   int detect_format(const char *line, int len);
 *   Trả về: 0 = plain, 1 = json, 2 = syslog
 *
 * Chỉ detect, không parse. Logic phải khớp với detector.py:
 * - json:   ký tự đầu (sau strip) là '{' và kết thúc bằng '}'
 * - syslog: khớp pattern "Mon DD HH:MM:SS host process..."
 * - plain:  còn lại
 */

#include <string.h>
#include <ctype.h>

#define FMT_PLAIN  0
#define FMT_JSON   1
#define FMT_SYSLOG 2

/* Bỏ whitespace đầu/cuối, trả về con trỏ đầu và độ dài mới */
static const char *strip(const char *s, int len, int *out_len) {
    int start = 0;
    int end = len;
    while (start < end && isspace((unsigned char)s[start])) start++;
    while (end > start && isspace((unsigned char)s[end - 1])) end--;
    *out_len = end - start;
    return s + start;
}

/* Kiểm tra 3 ký tự có phải tháng viết tắt không */
static int is_month(const char *s) {
    static const char *months[] = {
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    };
    for (int i = 0; i < 12; i++) {
        if (s[0] == months[i][0] && s[1] == months[i][1] && s[2] == months[i][2])
            return 1;
    }
    return 0;
}

/*
 * Detect syslog RFC 3164:
 *   Mon DD HH:MM:SS host ...
 *   Mon  D HH:MM:SS host ...
 */
static int is_syslog(const char *s, int len) {
    if (len < 15) return 0;
    if (!is_month(s)) return 0;

    int i = 3;
    if (s[i] != ' ') return 0;
    i++;

    /* 1 hoặc 2 chữ số ngày */
    if (!isdigit((unsigned char)s[i])) return 0;
    i++;
    if (i < len && isdigit((unsigned char)s[i])) i++;
    if (i >= len || s[i] != ' ') return 0;
    i++;

    /* HH:MM:SS */
    for (int k = 0; k < 8; k++) {
        if (i >= len) return 0;
        char c = s[i];
        if (k == 2 || k == 5) {
            if (c != ':') return 0;
        } else {
            if (!isdigit((unsigned char)c)) return 0;
        }
        i++;
    }

    /* Phải có ít nhất 1 space + hostname + space + process + ':' */
    if (i >= len || s[i] != ' ') return 0;
    return 1;
}

int detect_format(const char *line, int len) {
    if (line == NULL || len <= 0) return FMT_PLAIN;

    int stripped_len = 0;
    const char *s = strip(line, len, &stripped_len);
    if (stripped_len == 0) return FMT_PLAIN;

    /* JSON: bắt đầu bằng '{' và kết thúc bằng '}' */
    if (s[0] == '{' && s[stripped_len - 1] == '}') {
        return FMT_JSON;
    }

    if (is_syslog(s, stripped_len)) {
        return FMT_SYSLOG;
    }

    return FMT_PLAIN;
}

/* Batch API: đếm số dòng mỗi format trong mảng.
 * Trả về qua out_counts[3] = {plain, json, syslog}.
 */
void count_formats(const char **lines, const int *lens, int n, int *out_counts) {
    out_counts[0] = 0;
    out_counts[1] = 0;
    out_counts[2] = 0;
    for (int i = 0; i < n; i++) {
        int fmt = detect_format(lines[i], lens[i]);
        out_counts[fmt]++;
    }
}
