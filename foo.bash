#!/bin/bash
echo "before fall asleep"
echo "Nice morning!"
sleep 20
DIR=~/results
mkdir -p "$DIR"
LAST=`ls "$DIR" |python -c 'import sys;l=sys.stdin.read();print max(map(int, l.split()))'`
touch "$DIR"/$(( $LAST + 1 ))

