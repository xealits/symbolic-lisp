#!/bin/bash

#echo $@
#echo $0
#echo $1

# syntax: ${<the var name>-<default value>}
export test_option=${1}
#export test_command="python3 nsp_lis.py --test $test_option"
export test_command="pytest $test_option"

echo test_command  "$test_command"

$test_command
echo -------   END first run  -------

while inotifywait -e close_write -e move_self nsp_lis.py test*.py
do
  echo
  echo ------- UPDATE -------
  echo test_command  "$test_command"
  echo
  $test_command
  echo -------   END  -------
done