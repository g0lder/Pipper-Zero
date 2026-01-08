#!/usr/bin/env bash
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"
python3 "$SCRIPT_PATH/python/image.py" "$SCRIPT_PATH/resources/fakeAg/" --rotate 180
