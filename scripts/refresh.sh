SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"

python3 $SCRIPT_PATH/python/refresh.py
python3 $SCRIPT_PATH/../launcher.py
