ifeq ($(origin CC), default)
CC = gcc
endif

C_SOURCES := \
	tests/main.c \
	tests/files/c_source/c_source/oer.c

CFLAGS := \
	-Wall \
	-Wextra \
	-Wdouble-promotion \
	-Wfloat-equal \
	-Wformat=2 \
	-Wshadow \
	-Werror

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
	codespell -d $$(git ls-files | grep -v ietf | grep -v 3gpp)
	$(MAKE) test-c
	python3 -m pycodestyle $$(git ls-files "asn1tools/*.py")

.PHONY: test-c
test-c:
	$(CC) $(CFLAGS) -Wpedantic -std=c99 -O3 $(C_SOURCES) \
	    -o main
	./main

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
