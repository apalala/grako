test: grako_test examples


grako_test:
	python -u -m grako.test 2>&1


examples: regex_test antlr_test


regex_test:
	cd examples/regex; make -s clean; make -s test > /dev/null


antlr_test:
	cd examples/antlr2grako; make -s clean; make -s test > /dev/null


flake8:
	flake8


docs: tmp/grako_docs.zip


tmp/grako_docs.zip: tmp/index.html
	zip --junk-paths tmp/grako_docs.zip tmp/index.html


tmp/index.html: README.rst etc/style.css
	rst2html.py \
		--stylesheet-path etc/style.css \
		--embed-stylesheet \
		README.rst > tmp/index.html


cython:
	python setup.py build_ext --inplace
	python3 setup.py build_ext --inplace


clean: clean_cython
	find -name "__pycache__" | xargs rm -rf
	find -name "*.pyc" | xargs rm -f
	find -name "*.pyd" | xargs rm -f
	find -name "*.pyo" | xargs rm -f
	find -name "*.orig" | xargs rm -f
	rm -rf grako.egg-info
	rm -rf dist
	rm -rf build
	rm -rf .tox


clean_cython:
	find grako -name "*.so" | xargs rm -f
	find grako -name "*.c" | xargs rm -f


release_check: clean
	rst2html.py README.rst > /dev/null
	python setup.py sdist
	tox
	@echo version `python -m grako --version`


distributions: release_check
	python setup.py sdist --formats=gztar,zip
	python setup.py bdist_wheel --universal


upload: distributions
	twine upload dist/*
