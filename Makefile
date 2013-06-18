# payswarm-python

all:
	@echo "Hint: Try 'test' or 'cover' target"

clean:
	rm -rf cover

test: nose-test

unittest-test:
	python -m unittest discover

nose-test:
	nosetests tests/test*.py

cover:
	nosetests \
		--with-cover --cover-package=payswarm --cover-html \
		tests/test*.py

.PHONY: test unittest-test nose-test cover
