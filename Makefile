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
	codespell -d $$(git ls-files | grep -v ietf | grep -v 3gpp)
	python3 -m pycodestyle $$(git ls-files "asn1tools/*.py")

test-sdist:
	rm -rf dist
	python setup.py sdist
	cd dist && \
	mkdir test && \
	cd test && \
	tar xf ../*.tar.gz && \
	cd asn1tools-* && \
	python setup.py test

release-to-pypi:
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*
