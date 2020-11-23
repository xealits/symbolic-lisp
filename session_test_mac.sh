#!/bin/bash

# this is Mac version
# it depends on pytest and fswatch

#echo $@
#echo $0
#echo $1

# syntax: ${<the var name>-<default value>}
export test_option=${1}
export test_watch_more=${2-""}

export watch_files="sym_lis.py sym_lis2.py sym_repl.py tests/test*.py $test_watch_more"

export test_command="pytest $test_option"

export PYTHONPATH=.
echo PYTHONPATH $PYTHONPATH
echo watch_files   "$watch_files"
echo test_command  "$test_command"

$test_command
echo -------   END first run  -------

fswatch $watch_files | while read changed_file
# I do not use the changed file
# because I run all tests anyway
do
  echo
  echo ------- UPDATE -------
  echo test_command  "$test_command"
  echo
  $test_command
  echo -------   END  -------
done
