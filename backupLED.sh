#!/bin/bash
SHELL=4shell:/bin/bash
export SHELL
PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games:/bin:/usr/bin:xxx
export PATH
exec &> /home/pi/Desktop/LEDBoard-2/backup-logfile.txt
rclone -v sync "/home/pi/Desktop/LEDBoard-2" gdrive:LEDBoard-Toby --filter-from /home/pi/Desktop/LEDBoard-2/filter-file.txt

