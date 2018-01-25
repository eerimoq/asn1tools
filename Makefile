test:
	python2 setup.py test
	python3 setup.py test
	env PYTHONPATH=. python3 examples/benchmarks/packages.py
	env PYTHONPATH=. python3 examples/benchmarks/codecs.py
	env PYTHONPATH=. python3 examples/question/question.py
	codespell -d $$(git ls-files | grep -v ietf | grep -v 3gpp)

release-to-pypi:
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*
