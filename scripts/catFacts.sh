SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"
RANDOM_FACT=$(shuf -n 1 $SCRIPT_PATH/resources/cat_facts.txt)
python3 $SCRIPT_PATH/python/text.py --text "$RANDOM_FACT" 0 0 8
