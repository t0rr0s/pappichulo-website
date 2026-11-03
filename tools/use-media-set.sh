#!/bin/sh
# Put one media set on the page. Usage: sh tools/use-media-set.sh a
# or:                                   sh tools/use-media-set.sh b
# Mix and match instead: copy one file, e.g.
#   cp media/set-b/family-3.jpg media/family-3.jpg
set -e
SET="$1"
case "$SET" in
  a|b) ;;
  *) echo "Say which set: a or b"; exit 1 ;;
esac
DIR="media/set-$SET"
[ -d "$DIR" ] || { echo "No folder $DIR"; exit 1; }
cp "$DIR"/*.jpg "$DIR"/*.mp4 media/
echo "Set $SET is now on the page."
