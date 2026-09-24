# VWeatherStation Davis Bridge

A tiny, dependency-free bridge that reads a **Davis WeatherLink Live** console
on your local network and pushes readings to your
[VWeatherStation](https://vweatherstation.com) PWS — for Davis owners who
prefer not to use the WeatherLink v2 cloud API.

## Use it (Python — any OS)
1. Register a station at https://vweatherstation.com/pws/connect/ (get ID + Key).
2. Edit the CONFIG block in `davis_bridge.py` (your WeatherLink Live IP, Station ID, Key).
3. `python davis_bridge.py` — leave it running.

## Windows .exe (no Python needed)
GitHub Actions builds a standalone `davis_bridge.exe` — grab it from the
**Actions** tab or a **Release**. Edit the CONFIG at the top of the script
before building, or use the Python version and pass config.

## What it does
Reads the WeatherLink Live local API (`http://<ip>/v1/current_conditions`),
converts the readings, and uploads them to `pws.vweatherstation.com` using the
Weather Underground protocol every 60 seconds.
