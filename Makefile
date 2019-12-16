# handy commands

# leave focus_file empty to run all tests
# or pass a string with files to run
testup: focus_file=
testup:
	./test_session.sh ${focus_file}

# just to remember it
test:
	pytest

# make test_coverage options="--cov-report term-missing"
# make test_coverage options="--cov-report annotate"
test_coverage: module=nsp_lis
test_coverage: options=
test_coverage:
	pytest ./ --cov ${module}  ${options}


