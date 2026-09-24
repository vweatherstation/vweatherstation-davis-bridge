#!/usr/bin/env python3
"""
VWeatherStation Davis Bridge — a tiny, dependency-free bridge that reads a
Davis WeatherLink Live (WLL) console on your local network and pushes readings
to your VWeatherStation PWS. For Davis owners who prefer not to use the
WeatherLink v2 cloud API.

Requirements: Python 3.8+ (standard library only).

SETUP:
  1. Find your WeatherLink Live device IP on your LAN (e.g. 192.168.1.50).
     It serves a local API at http://<ip>:80/v1/current_conditions
  2. Register a station at https://vweatherstation.com/pws/connect/ to get
     your Station ID + Key.
  3. Fill in the CONFIG below.
  4. Run:  python davis_bridge.py
     Leave it running (or set it as a service / scheduled task).
"""
import json, time, urllib.request, urllib.parse, sys

# ================= CONFIG =================
WLL_IP       = "192.168.1.50"        # your WeatherLink Live device IP on the LAN
STATION_ID   = "YOUR_STATION_ID"     # from vweatherstation.com/pws/connect
STATION_KEY  = "YOUR_STATION_KEY"
UPLOAD_HOST  = "pws.vweatherstation.com"
INTERVAL_SEC = 60                    # how often to push (>=30)
# =========================================

def get_wll():
    """Read current conditions from the WeatherLink Live local API."""
    url = f"http://{WLL_IP}:80/v1/current_conditions"
    with urllib.request.urlopen(url, timeout=8) as r:
        return json.loads(r.read().decode())

def extract(data):
    """Pull the fields we need from the WLL JSON (ISS sensor)."""
    out = {}
    for cond in data.get("data", {}).get("conditions", []):
        t = cond.get("data_structure_type")
        if t == 1:  # ISS current conditions
            if cond.get("temp") is not None:        out["tempf"] = cond["temp"]
            if cond.get("hum") is not None:         out["humidity"] = cond["hum"]
            if cond.get("wind_speed_last") is not None: out["windspeedmph"] = cond["wind_speed_last"]
            if cond.get("wind_dir_last") is not None:    out["winddir"] = cond["wind_dir_last"]
            if cond.get("wind_speed_hi_last_10_min") is not None: out["windgustmph"] = cond["wind_speed_hi_last_10_min"]
            if cond.get("rain_rate_last_in") is not None: out["rainin"] = cond["rain_rate_last_in"]
            if cond.get("rainfall_daily_in") is not None: out["dailyrainin"] = cond["rainfall_daily_in"]
            if cond.get("dew_point") is not None:   out["dewptf"] = cond["dew_point"]
            if cond.get("solar_rad") is not None:   out["solarradiation"] = cond["solar_rad"]
            if cond.get("uv_index") is not None:    out["UV"] = cond["uv_index"]
        elif t == 3:  # barometer
            if cond.get("bar_sea_level") is not None: out["baromin"] = cond["bar_sea_level"]
    return out

def push(fields):
    """Upload to VWeatherStation using the Weather Underground protocol."""
    params = {"ID": STATION_ID, "PASSWORD": STATION_KEY, "action": "updateraw"}
    params.update(fields)
    url = f"http://{UPLOAD_HOST}/pws/upload.php?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=8) as r:
        return r.read().decode().strip()

def main():
    print(f"VWeatherStation Davis Bridge -> reading {WLL_IP}, pushing to {UPLOAD_HOST} every {INTERVAL_SEC}s")
    if STATION_ID.startswith("YOUR_"):
        print("ERROR: set STATION_ID and STATION_KEY in the CONFIG section first."); sys.exit(1)
    while True:
        try:
            data = get_wll()
            fields = extract(data)
            if fields:
                resp = push(fields)
                print(time.strftime("%H:%M:%S"), "pushed:", fields.get("tempf"), "F ->", resp)
            else:
                print(time.strftime("%H:%M:%S"), "no data parsed from WLL")
        except Exception as e:
            print(time.strftime("%H:%M:%S"), "error:", e)
        time.sleep(max(30, INTERVAL_SEC))

if __name__ == "__main__":
    main()
