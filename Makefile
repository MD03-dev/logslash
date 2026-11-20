# Makefile cho logslash.

PYTHON ?= python

.PHONY: help test build bench clean install setup bench-quick run-demo

help:
	@echo "logslash Makefile"
	@echo ""
	@echo "  make setup       - Setup day du"
	@echo "  make build       - Build C module"
	@echo "  make test        - Chay toan bo test"
	@echo "  make bench       - Benchmark (repeat 1000)"
	@echo "  make bench-quick - Benchmark (repeat 100)"
	@echo "  make install     - Cai lenh toan cuc"
	@echo "  make clean       - Xoa file build"
	@echo "  make run-demo    - Chay demo"

setup:
	@bash scripts/setup.sh

build:
	@bash scripts/build_c.sh

test:
	@bash scripts/test_all.sh

bench:
	@$(PYTHON) -m logslash bench tests/sample3.log --repeat 1000

bench-quick:
	@$(PYTHON) -m logslash bench tests/sample3.log --repeat 100

install:
	@bash scripts/install.sh

clean:
	@echo "Don dep..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -f logslash/libcdetect.so
	@echo "Xong"

run-demo:
	@echo "=== 1. Detect format ==="
	@$(PYTHON) -m logslash detect tests/sample.log
	@echo ""
	@echo "=== 2. Parse NDJSON ==="
	@$(PYTHON) -m logslash parse tests/sample3.log --limit 2
	@echo ""
	@echo "=== 3. Filter + table ==="
	@$(PYTHON) -m logslash filter tests/sample3.log --level-min warn -o table
	@echo ""
	@echo "=== 4. CSV ==="
	@$(PYTHON) -m logslash parse tests/sample3.log -o csv --limit 2
