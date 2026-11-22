#!/bin/bash
# usage: lines of "NN session gen signature" on stdin
B="https://elevenlabsusercontent.com/database/workspace/3aa18f01d0004b35a785dba8af0f0fca/content_generation"
Q="content.mp3?Expires=1795356000&KeyName=assets-cdn-key-1&Signature="
while read n s g sig; do [ -z "$n" ] && continue; curl -sS -o L$n.mp3 "$B/$s/$g/$Q$sig" && echo "L$n $(ffprobe -v error -show_entries format=duration -of csv=p=0 L$n.mp3)" || echo FAIL $n; done
