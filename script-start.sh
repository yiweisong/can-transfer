#!/bin/bash
nohup python3 ./main.py & echo $! > pidfile.txt
