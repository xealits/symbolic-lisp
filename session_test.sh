#!/bin/bash

# this is Linux version
# it depends on pytest and inotifywait

#echo $@
#echo $0
#echo $1

# syntax: ${<the var name>-<default value>}
export test_option=${1}
export test_watch_more=${2-""}

export watch_files="sym_lis.py sym_lis2.py sym_lis3.py sym_repl.py tests/test*.py $test_watch_more"

export test_command="pytest $test_option"

export PYTHONPATH=.
echo PYTHONPATH $PYTHONPATH
echo watch_files   "$watch_files"
echo test_command  "$test_command"

$test_command
echo -------   END first run  -------

while inotifywait -e close_write -e move_self $watch_files
do
  echo
  echo ------- UPDATE -------
  echo test_command  "$test_command"
  echo
  $test_command
  echo -------   END  -------
done
