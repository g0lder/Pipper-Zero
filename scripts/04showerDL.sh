#!/bin/sh

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"
RSS="$SCRIPT_PATH/resources/showerthoughts.rss"
OUT="$SCRIPT_PATH/resources/showerthoughts.txt"

curl --silent \
  -A "showerthoughts-script/1.0" \
  https://www.reddit.com/r/showerthoughts/.rss \
  --output "$RSS"

xmlstarlet sel \
  -N atom="http://www.w3.org/2005/Atom" \
  -t -m "//atom:entry/atom:title" \
  -v "normalize-space(.)" -n \
  "$RSS" > "$OUT"

rm "$RSS"
