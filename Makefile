test: grako_test examples

grako_test:
	python -u -m grako.test 2>&1

examples: regex_test antlr_test

regex_test:
	cd examples/regex; make -s clean; make -s test > /dev/null

antlr_test:
	cd examples/antlr2grako; make -s clean; make -s test > /dev/null

flake8:
	flake8 --exclude .tox,docs,tmp,.ropeproject --max-line-length 200

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
