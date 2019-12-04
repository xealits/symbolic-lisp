#!/bin/bash

while inotifywait -e close_write -e move_self nsp_lis.py; do python3 nsp_lis.py --test 1; done
