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
	tests/files/c_source/c_source/uper.c

CFLAGS = \
	-O3 \
	-std=c99 \
	-Wall \
	-Wextra \
	-Wpedantic \
	-Wdouble-promotion \
	-Wfloat-equal \
	-Wformat=2 \
	-Wshadow \
	-Werror

MASSIF_FLAGS = --tool=massif --time-unit=B --stacks=yes

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
	codespell -d $$(git ls-files | grep -v ietf | grep -v 3gpp | grep -v generated)
	python3 -m pycodestyle $$(git ls-files "asn1tools/*.py")

.PHONY: test-c-oer
test-c-oer:
	$(CC) $(CFLAGS) -Itests/files/c_source $(OER_C_SOURCES) -o $(OER_EXE)
	size $(OER_EXE)
	rm -f $(OER_EXE).massif
	valgrind $(MASSIF_FLAGS) --massif-out-file=$(OER_EXE).massif ./$(OER_EXE)
	ms_print $(OER_EXE).massif

.PHONY: test-c-uper
test-c-uper:
	$(CC) $(CFLAGS) $(UPER_C_SOURCES) -o $(UPER_EXE)
	size $(UPER_EXE)
	rm -f $(UPER_EXE).massif
	valgrind $(MASSIF_FLAGS) --massif-out-file=$(UPER_EXE).massif ./$(UPER_EXE)
	ms_print $(UPER_EXE).massif

.PHONY: test-c
test-c:
	$(MAKE) test-c-oer
	$(MAKE) test-c-uper

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
