test:
	python2 setup.py test
	python3 setup.py test
	env PYTHONPATH=. python3 examples/benchmarks/packages/ber.py
	env PYTHONPATH=. python3 examples/benchmarks/packages/uper.py
	env PYTHONPATH=. python3 examples/benchmarks/codecs.py
	env PYTHONPATH=. python3 examples/benchmarks/question/question.py
	env PYTHONPATH=. python3 examples/hello_world.py
	codespell -d $$(git ls-files | grep -v ietf | grep -v 3gpp)
	python3 -m pycodestyle $$(git ls-files "asn1tools/*.py")

release-to-pypi:
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*
