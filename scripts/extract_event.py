#!/usr/bin/env python3

#!/usr/bin/env python3

import os
import re
from collections import defaultdict
from models import Station, StationReading, Event
from parse_station import parse_station_file
from pathlib import Path


def extract_event(root_dir: str, event_id: str) -> Event:
    stations = extract_all_stations(root_dir)
    event = Event(event_id=event_id)

    # Try to fill in event-level metadata from the first station/reading
    for station in stations.values():
        if station.readings:
            sample_reading = next(iter(station.readings.values()))
            event.origin_time = sample_reading.origin_time
            event.latitude = sample_reading.latitude
            event.longitude = sample_reading.longitude
            event.depth_km = sample_reading.depth_km
            event.magnitude = sample_reading.magnitude
            break

    for station in stations.values():
        event.add_station(station)

    return event


def is_station_file(filename):
    return re.match(r"^([A-Z0-9]+)\d{12}\.(EW|NS|UD)[12]?$", filename)


def extract_all_stations(root_dir: str) -> dict[str, Station]:
    stations: dict[str, Station] = {}

    pattern = re.compile(r"^([A-Z]{4}\d{2}|\w{3}\d{3})\d*\.(EW|NS|UD)([12]?)$")
    # pattern = re.compile(r"^([A-Z]{3}\d{3})\d*\.(EW|NS|UD)([12]?)$")

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if not is_station_file(file):
                continue

            match = pattern.match(file)
            if not match:
                continue

            station_base, direction, suffix = match.groups()
            direction_full = direction + suffix

            if station_base not in stations:
                stations[station_base] = Station(station_base)

            filepath = os.path.join(subdir, file)
            try:
                metadata, data = parse_station_file(filepath)
                reading = StationReading.from_dict(metadata, data)
                stations[station_base].add_reading(direction_full, reading)
            except Exception as e:
                print(f"[!] Failed to parse {file}: {e}")

    return stations


if __name__ == "__main__":
    import sys
    import json

    # if len(sys.argv) < 2:
    #     print("Usage: python extract_all_stations.py <ROOT_FOLDER>")
    #     sys.exit(1)

    # root = os.path.abspath(sys.argv[1])
    # stations = extract_all_stations(root)

    # print(f"Loaded {len(stations)} stations.")
    # for name, station in stations.items():
    #     print(f"- {name}: {station.directions()}")

    if len(sys.argv) < 3:
        print("Usage: python extract_event.py <PATH> <EVENT_ID>")
        sys.exit(1)

    event = extract_event(sys.argv[1], sys.argv[2])
    print(event)
    for name, station in event.stations.items():
        print(f"  {name}: {station.directions()}")
