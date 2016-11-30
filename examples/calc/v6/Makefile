start: test


test: clean parser model
	PYTHONPATH=../../.. python calc_parser.py ../input.txt
	PYTHONPATH=../../.. python calc.py ../input.txt


parser: calc_parser.py


model: calc_model.py


calc_parser.py: calc.ebnf
	PYTHONPATH=../../.. python -m grako -o $@ $< 2>&1


calc_model.py: calc.ebnf
	PYTHONPATH=../../.. python -m grako -g -o $@ $< 2>&1


clean:
	-@rm -f calc/calc_parser.py
