#!/bin/bash
pid_file=pidfile.txt
kill `cat ./$pid_file`
rm -rf ./$pid_file ./nohup.out