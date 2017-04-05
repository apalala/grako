# Copyright (C) 2017      by Juancarlo Añez
# Copyright (C) 2012-2016 by Juancarlo Añez and Thomas Bragg

start: test

test: clean parser
	PYTHONPATH=../../.. python calc_parser.py ../input.txt

parser: calc_parser.py

calc_parser.py: calc.ebnf
	PYTHONPATH=../../.. python -m grako -o $@ $< 2>&1

clean:
	-@rm -f calc/calc_parser.py
