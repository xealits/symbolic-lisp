# handy commands

# leave focus_file empty to run all tests
# or pass a string with files to run
testup: focus_file=
testup: watch_more=
testup:
	./session_test.sh tests/${focus_file} ${watch_more}

# just to remember it
test:
	PYTHONPATH=. pytest

# make test_coverage options="--cov-report term-missing"
# make test_coverage options="--cov-report annotate"
test_coverage: module=sym_lis
test_coverage: options=
test_coverage:
	PYTHONPATH=. pytest ./ --cov ${module}  ${options}
