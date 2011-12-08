#!/bin/bash

# Replace these three settings.
PROJDIR="`pwd`"
PIDFILE="$PROJDIR/logs/fcgi.pid"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    sudo kill `cat -- $PIDFILE`
    sudo rm -f -- $PIDFILE
fi