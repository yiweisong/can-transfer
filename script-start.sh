#!/bin/bash
nohup python3 -u ./main.py > status.log 2>&1 & echo $! > pidfile.txt
