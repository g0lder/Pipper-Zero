#!/usr/bin/bash
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"
# =======================
# USER INPUT
# =======================
LOCATION="Boulder, CO"

# =======================
# GEOCODE via Nominatim
# =======================
GEO_JSON=$(curl -sG "https://nominatim.openstreetmap.org/search" \
  --data-urlencode "q=$LOCATION" \
  --data-urlencode "format=json")

LAT=$(echo "$GEO_JSON" | jq -r '.[0].lat // empty')
LON=$(echo "$GEO_JSON" | jq -r '.[0].lon // empty')

if [[ -z "$LAT" || -z "$LON" ]]; then
  echo "Geocoding failed"
  exit 1
fi

# =======================
# OPEN-METEO HOURLY FORECAST (12h)
# =======================
WEATHER_JSON=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=$LAT&longitude=$LON&hourly=temperature_2m,windspeed_10m,precipitation,cloudcover&temperature_unit=fahrenheit&windspeed_unit=mph&timezone=auto")

# =======================
# PRINT NEXT 12 HOURS
# =======================
for i in $(seq 0 11); do
  TIME=$(echo "$WEATHER_JSON" | jq -r ".hourly.time[$i]")
  TEMP=$(echo "$WEATHER_JSON" | jq -r ".hourly.temperature_2m[$i]")
  WIND=$(echo "$WEATHER_JSON" | jq -r ".hourly.windspeed_10m[$i]")
  RAIN=$(echo "$WEATHER_JSON" | jq -r ".hourly.precipitation[$i]")
  CLOUD=$(echo "$WEATHER_JSON" | jq -r ".hourly.cloudcover[$i]")

  # Store multi-line string in variable weather_1..weather_12
  declare "weather_$((i+1))=$TIME Temp: ${TEMP}F  Wind: ${WIND} mph  Rain: ${RAIN} mm  Cloud cover: ${CLOUD}%"
done

python3 "$SCRIPT_PATH/python/text.py" --text "$weather_1" 0 0 15
sleep 15
python3 "$SCRIPT_PATH/../launcher.py"
