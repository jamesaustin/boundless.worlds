#!/usr/bin/env make

APP=patterns.py
OPTIONS=--path output
LOGS=logs
OPEN=open
GITHUB_URL=https://github.com/turbulenz/boundless.worlds
PYTHON=python3

all:
	@-mkdir -p $(LOGS)
	@$(PYTHON) $(APP) $(OPTIONS) > $(LOGS)/test.1.txt
	@diff $(LOGS)/test.txt $(LOGS)/test.1.txt | tee $(LOGS)/diff.1.txt

base:
	@-mkdir -p $(LOGS)
	@$(PYTHON) $(APP) $(OPTIONS) > $(LOGS)/test.txt

check:
	@-mkdir -p $(LOGS)
	@pylint --rcfile .pylintrc $(wildcard *.py) | tee $(LOGS)/pylint.txt

edit:
	@$(EDITOR) .

github:
	@$(OPEN) $(GITHUB_URL)

-include make/*.mk
