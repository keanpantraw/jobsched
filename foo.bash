#!/bin/bash
echo "huj"
sleep 20
echo "her"
echo "da vsem poher"
DIR=~/results
mkdir -p "$DIR"
LAST=`ls "$DIR" |python -c 'import sys;l=sys.stdin.read();print max(map(int, l.split()))'`
touch "$DIR"/$(( $LAST + 1 ))

