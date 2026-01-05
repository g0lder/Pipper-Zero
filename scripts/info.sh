#!/usr/bin/env bash
read -r IFACE IP <<<"$(ip route get 1 | awk '{for(i=1;i<=NF;i++) if($i=="dev"){d=$(i+1)} else if($i=="src"){s=$(i+1)} } END{print d, s}')"
SSID=$(iwconfig "$IFACE" | grep ESSID | awk '{print $4}' | awk -F':' '{print $2}' | sed 's/"//g')
CONNECTION=$(ping -c 5 8.8.8.8)
if [[ $? -eq 0 ]]; then
  CONNECTION=true
else
  CONNECTION=false
fi
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"

sudo $SCRIPT_PATH/python/text.py  \
	--text "IP Address: "$IP 0 0 10 \
	--text "Interface:  "$IFACE 0 10 10\
	--text "Service SID:"$SSID 0 20 10\
	--text "Connected:  "$CONNECTION 0 30 10

sleep 15

sudo $SCRIPT_PATH/../launcher.py
