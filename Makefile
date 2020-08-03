ifeq ($(origin CC), default)
CC = gcc
endif

C_SOURCES := \
	tests/files/c_source/oer.c
	# tests/files/c_source/uper.c

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

CFLAGS := \
	-Wall \
	-Wextra \
	-Wdouble-promotion \
	-Wfloat-equal \
	-Wformat=2 \
	-Wshadow \
	-Werror

CFLAGS_EXTRA := \
	-Wduplicated-branches \
	-Wduplicated-cond \
	-Wjump-misses-init \
	-Wlogical-op \
	-Wnull-dereference \
	-Wrestrict \
	-Wconversion \
	-Wpedantic

CFLAGS_EXTRA_CLANG := \
	-fsanitize=address \
	-fsanitize=undefined,nullability \
	-Warray-bounds-pointer-arithmetic \
	-Wassign-enum \
	-Wcast-align \
	-Wcast-qual \
	-Wchar-subscripts \
	-Wcomma \
	-Wcomment \
	-Wconditional-uninitialized \
	-Wdate-time \
	-Wdocumentation \
	-Wduplicate-decl-specifier \
	-Wduplicate-enum \
	-Wduplicate-method-arg \
	-Wduplicate-method-match \
	-Wembedded-directive \
	-Wempty-translation-unit \
	-Wexpansion-to-defined \
	-Wflexible-array-extensions \
	-Wfloat-conversion \
	-Wfloat-equal \
	-Wfloat-overflow-conversion \
	-Wfloat-zero-conversion \
	-Wformat-non-iso \
	-Wformat-nonliteral \
	-Wformat-pedantic \
	-Wfour-char-constants \
	-Wgnu-anonymous-struct \
	-Wgnu-array-member-paren-init \
	-Wgnu-auto-type \
	-Wgnu-binary-literal \
	-Wgnu-case-range \
	-Wgnu-complex-integer \
	-Wgnu-compound-literal-initializer \
	-Wgnu-conditional-omitted-operand \
	-Wgnu-designator \
	-Wgnu-empty-initializer \
	-Wgnu-empty-struct \
	-Wgnu-flexible-array-initializer \
	-Wgnu-flexible-array-union-member \
	-Wgnu-folding-constant \
	-Wgnu-imaginary-constant \
	-Wgnu-include-next \
	-Wgnu-label-as-value \
	-Wgnu-redeclared-enum \
	-Wgnu-statement-expression \
	-Wgnu-union-cast \
	-Wgnu-zero-line-directive \
	-Wgnu-zero-variadic-macro-arguments \
	-Wheader-hygiene \
	-Widiomatic-parentheses \
	-Wimplicit \
	-Wimplicit-fallthrough \
	-Wloop-analysis \
	-Wmethod-signatures \
	-Wmissing-braces \
	-Wmissing-field-initializers \
	-Wnested-anon-types \
	-Wnewline-eof \
	-Wnull-pointer-arithmetic \
	-Woverlength-strings \
	-Wpointer-arith \
	-Wsign-compare \
	-Wtautological-compare \
	-Wundef \
	-Wuninitialized \
	-Wunreachable-code \
	-Wunreachable-code-aggressive \
	-Wunused-comparison \
	-Wunused-const-variable \
	-Wunused-parameter \
	-Wunused-variable \
	-Wvariadic-macros \
	-Wzero-as-null-pointer-constant \
	-Wzero-length-array

.PHONY: test
test:
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
	python3 -m pycodestyle $$(git ls-files "asn1tools/*.py")

.PHONY: codespell
codespell:
	codespell -d $$(git ls-files | grep -v ietf \
				     | grep -v 3gpp \
				     | grep -v generated \
				     | grep -v "\\.rs" \
				     | grep -v asn1tools/source/rust \
				     | grep -v "\.asn")

.PHONY: test-c
test-c:
	for f in $(C_SOURCES) ; do \
	    $(CC) $(CFLAGS) $(CFLAGS_EXTRA) -std=c99 -O3 -c $$f ; \
	    clang $(CFLAGS) $(CFLAGS_EXTRA_CLANG) -std=c99 -O3 -c $$f ; \
	done

	$(MAKE) -C tests

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
