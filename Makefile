test: grako_test examples


grako_test:
	python -u -m grako.test 2>&1


examples: regex_test antlr_test


regex_test:
	cd examples/regex; make -s clean; make -s test > /dev/null


antlr_test:
	cd examples/antlr2grako; make -s clean; make -s test > /dev/null


flake8:
	flake8 --exclude .tox,docs,tmp,.ropeproject,build --max-line-length 200


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
	find grako -name "__pycache__" | xargs rm -rf
	find grako -name "*.pyc" | xargs rm -f
	find grako -name "*.pyo" | xargs rm -f
	find grako -name "*.orig" | xargs rm -f
	find examples -name "__pycache__" | xargs rm -rf
	find examples -name "*.pyc" | xargs rm -f
	find examples -name "*.pyo" | xargs rm -f
	find examples -name "*.orig" | xargs rm -f


clean_cython:
	find grako -name "*.so" | xargs rm -f
	find grako -name "*.c" | xargs rm -f


release_check: flake8
	rst2html.py README.rst > /dev/null
	python setup.py sdist
	tox
	@echo version `python -m grako --version`


publish: release_check
	python setup.py sdist --formats=gztar,zip
	python setup.py bdist_wheel --universal


upload: release_check
	python setup.py sdist --formats=gztar,zip bdist_wheel --universal register upload
