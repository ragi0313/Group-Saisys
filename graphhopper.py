#!/usr/bin/env python3
# graphhopper_app.py
# Final script for "Integrate a REST API in a Python Application" lab

import os
import requests
import urllib.parse

ROUTE_URL = "https://graphhopper.com/api/1/route?"
GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"

# Prefer env var; fall back to literal if set
API_KEY = os.getenv("GRAPHHOPPER_API_KEY")  # set GRAPHHOPPER_API_KEY in your shell

def geocoding(location: str, key: str):
    """
    Look up lat/lng for a location string using Graphhopper Geocoding API.
    Returns: (status_code, lat, lng, pretty_location)
             lat/lng are 'null' (as strings) on error.
    """
    while location == "":
        location = input("Enter the location again: ")

    url = GEOCODE_URL + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    reply = requests.get(url)
    status = reply.status_code

    try:
        data = reply.json()
    except Exception:
        data = {}

    if status == 200 and isinstance(data.get("hits"), list) and len(data["hits"]) != 0:
        hit = data["hits"][0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        name = hit.get("name", location)
        value = hit.get("osm_value", "")
        country = hit.get("country", "")
        state = hit.get("state", "")

        if state and country:
            pretty = f"{name}, {state}, {country}"
        elif country:
            pretty = f"{name}, {country}"
        else:
            pretty = name

        print(f"Geocoding API URL for {pretty} (Location Type: {value})\n{url}")
        return status, lat, lng, pretty

    lat = "null"
    lng = "null"
    pretty = location

    if status != 200:
        msg = data.get("message", "Unknown error")
        print(f"Geocode API status: {status}\nError message: {msg}")
    else:
        print(f"Geocoding API URL for {pretty}\n{url}")
        print("No results found for that location.")

    return status, lat, lng, pretty


def main():
    profiles = ["car", "bike", "foot"]

    while True:
        print("\n+++++++++++++++++++++++++++++++++++++++++++++")
        print("Vehicle profiles available on Graphhopper:")
        print("+++++++++++++++++++++++++++++++++++++++++++++")
        print("car, bike, foot")
        print("+++++++++++++++++++++++++++++++++++++++++++++")

        vehicle = input("Enter a vehicle profile from the list above: ").strip()
        if vehicle in ("q", "quit"):
            break
        elif vehicle not in profiles:
            print("No valid vehicle profile was entered. Using the car profile.")
            vehicle = "car"

        # --- Origin ---
        loc1 = input("Starting Location: ").strip()
        if loc1 in ("q", "quit"):
            break
        orig = geocoding(loc1, API_KEY)

        # --- Destination ---
        loc2 = input("Destination: ").strip()
        if loc2 in ("q", "quit"):
            break
        dest = geocoding(loc2, API_KEY)

        print("=================================================")

        if orig[0] == 200 and dest[0] == 200 and orig[1] != "null" and dest[1] != "null":
            op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
            dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
            paths_url = ROUTE_URL + urllib.parse.urlencode({"key": API_KEY, "vehicle": vehicle}) + op + dp

            route_resp = requests.get(paths_url)
            paths_status = route_resp.status_code
            try:
                paths_data = route_resp.json()
            except Exception:
                paths_data = {}

            print(f"Routing API Status: {paths_status}\nRouting API URL:\n{paths_url}")
            print("=================================================")
            print(f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
            print("=================================================")

            if paths_status == 200 and "paths" in paths_data and len(paths_data["paths"]) > 0:
                path0 = paths_data["paths"][0]

                km = path0["distance"] / 1000.0
                miles = km / 1.60934  # more precise

                total_ms = int(path0["time"])
                sec = int((total_ms / 1000) % 60)
                minutes = int((total_ms / 1000) / 60 % 60)
                hours = int((total_ms / 1000) / 60 / 60)

                print("Distance Traveled: {0:.1f} miles / {1:.1f} km".format(miles, km))
                print("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hours, minutes, sec))
                print("=================================================")

                instructions = path0.get("instructions", [])
                for step in instructions:
                    text = step.get("text", "")
                    dist_m = float(step.get("distance", 0.0))
                    print("{0} ( {1:.1f} km / {2:.1f} miles )".format(
                        text, dist_m / 1000.0, dist_m / 1000.0 / 1.60934
                    ))
                print("=================================================")
            else:
                msg = paths_data.get(
                    "message",
                    "Connection between locations not found or another error occurred."
                )
                print("Error message: " + msg)
                print("***********************************************")
        else:
            print("Could not geocode one or both locations. Please try again.")


if __name__ == "__main__":
    main()
