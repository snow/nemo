#!/bin/bash

# Replace these three settings.
PROJDIR="`pwd`"
PIDFILE="$PROJDIR/logs/fcgi.pid"

cd $PROJDIR
sudo ./stop.sh
sudo ./manage.py runfcgi pidfile=$PIDFILE host=127.0.0.1 port=3021 #daemonize=false