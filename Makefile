ifeq ($(origin CC), default)
CC = gcc
endif

OER_EXE = main_oer
UPER_EXE = main_uper
OER_C_SOURCES = \
	tests/main_oer.c \
	tests/files/c_source/oer.c \
	tests/files/c_source/c_source-minus.c
UPER_C_SOURCES = \
	tests/main_uper.c \
	tests/files/c_source/uper.c \
	tests/files/c_source/boolean_uper.c \
	tests/files/c_source/octet_string_uper.c
CFLAGS = \
	-Itests/files/c_source \
	-std=c99 \
	-Wall \
	-Wextra \
	-Wpedantic \
	-Wdouble-promotion \
	-Wfloat-equal \
	-Wsign-conversion \
	-Wformat=2 \
	-Wshadow \
	-Werror \
	-pg \
	-fprofile-arcs \
	-ftest-coverage

FUZZER_CC ?= clang
FUZZER_OER_EXE = main_oer_fuzzer
FUZZER_UPER_EXE = main_uper_fuzzer
FUZZER_OER_C_SOURCES = \
	tests/main_oer_fuzzer.c \
	tests/files/c_source/oer.c
FUZZER_UPER_C_SOURCES = \
	tests/main_uper_fuzzer.c \
	tests/files/c_source/uper.c
FUZZER_CFLAGS = \
	-fprofile-instr-generate \
	-fcoverage-mapping \
	-Itests/files/c_source \
	-g -fsanitize=address,fuzzer \
	-fsanitize=signed-integer-overflow \
	-fno-sanitize-recover=all
FUZZER_EXECUTION_TIME ?= 30

.PHONY: test
test:
	python2 setup.py test
	python3 setup.py test
	$(MAKE) test-sdist
	env PYTHONPATH=. python3 examples/benchmarks/packages/ber.py
	env PYTHONPATH=. python3 examples/benchmarks/packages/uper.py
	env PYTHONPATH=. python3 examples/benchmarks/codecs.py
	env PYTHONPATH=. python3 examples/benchmarks/compile_methods.py
	env PYTHONPATH=. python3 examples/benchmarks/question/question.py
	env PYTHONPATH=. python3 examples/hello_world.py
	env PYTHONPATH=. python3 examples/x509_pem.py
	env PYTHONPATH=. python3 examples/compact_extensions_uper/main.py
	env PYTHONPATH=. python3 examples/programming_types/main.py
	$(MAKE) test-c
	env FUZZER_EXECUTION_TIME=1 $(MAKE) test-c-fuzzer
	$(MAKE) -C examples/benchmarks/c_source
	codespell -d $$(git ls-files | grep -v ietf \
	                             | grep -v 3gpp \
	                             | grep -v generated \
	                             | grep -v "\\.rs" \
	                             | grep -v asn1tools/source/rust)
	python3 -m pycodestyle $$(git ls-files "asn1tools/*.py")

.PHONY: test-c-oer
test-c-oer:
	$(CC) $(CFLAGS) $(OER_C_SOURCES) -o $(OER_EXE)
	size $(OER_EXE)
	./$(OER_EXE)

.PHONY: test-c-uper
test-c-uper:
	$(CC) $(CFLAGS) $(UPER_C_SOURCES) -o $(UPER_EXE)
	size $(UPER_EXE)
	./$(UPER_EXE)

.PHONY: test-c
test-c:
	$(MAKE) test-c-oer
	$(MAKE) test-c-uper

.PHONY: test-c-oer-fuzzer-run
test-c-oer-fuzzer-run:
	$(FUZZER_CC) $(FUZZER_CFLAGS) $(FUZZER_OER_C_SOURCES) -o $(FUZZER_OER_EXE)
	rm -f $(FUZZER_OER_EXE).profraw
	LLVM_PROFILE_FILE="$(FUZZER_OER_EXE).profraw" \
	    ./$(FUZZER_OER_EXE) \
	    -max_total_time=$(FUZZER_EXECUTION_TIME) \
	    -print_final_stats
	llvm-profdata merge \
	    -sparse $(FUZZER_OER_EXE).profraw \
	    -o $(FUZZER_OER_EXE).profdata
	llvm-cov show ./$(FUZZER_OER_EXE) \
	    -instr-profile=$(FUZZER_OER_EXE).profdata

.PHONY: test-c-uper-fuzzer-run
test-c-uper-fuzzer-run:
	$(FUZZER_CC) $(FUZZER_CFLAGS) $(FUZZER_UPER_C_SOURCES) -o $(FUZZER_UPER_EXE)
	rm -f $(FUZZER_UPER_EXE).profraw
	LLVM_PROFILE_FILE="$(FUZZER_UPER_EXE).profraw" \
	    ./$(FUZZER_UPER_EXE) \
	    -max_total_time=$(FUZZER_EXECUTION_TIME) \
	    -print_final_stats
	llvm-profdata merge \
	    -sparse $(FUZZER_UPER_EXE).profraw \
	    -o $(FUZZER_UPER_EXE).profdata
	llvm-cov show ./$(FUZZER_UPER_EXE) \
	    -instr-profile=$(FUZZER_UPER_EXE).profdata

.PHONY: test-c-fuzzer
test-c-fuzzer:
	$(MAKE) test-c-oer-fuzzer-run
	$(MAKE) test-c-uper-fuzzer-run
	echo
	echo "REPORT:"
	echo
	llvm-cov report ./$(FUZZER_OER_EXE) \
	    -instr-profile=$(FUZZER_OER_EXE).profdata
	echo
	llvm-cov report ./$(FUZZER_UPER_EXE) \
	    -instr-profile=$(FUZZER_UPER_EXE).profdata

.PHONY: test-rust
test-rust:
	cd tests/rust_source && cargo run

.PHONY: test-sdist
test-sdist:
	rm -rf dist
	python setup.py sdist
	cd dist && \
	mkdir test && \
	cd test && \
	tar xf ../*.tar.gz && \
	cd asn1tools-* && \
	python setup.py test

.PHONY: release-to-pypi
release-to-pypi:
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*
