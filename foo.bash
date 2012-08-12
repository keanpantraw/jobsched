#!/bin/bash
echo "before fall asleep"
sleep 20
echo "Nice morning!"
DIR=~/results
mkdir -p "$DIR"
LAST=`ls "$DIR" |python -c 'import sys;l=sys.stdin.read();print max(map(int, l.split()))'`
touch "$DIR"/$(( $LAST + 1 ))

