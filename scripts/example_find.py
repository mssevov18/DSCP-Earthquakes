#!/usr/bin/env python3

import sys
import os
from parse_station import extract_for_station

if len(sys.argv) < 3:
    print("Usage: python example_find.py <PATH> <STATION_NAME>")
    sys.exit(1)

path = os.path.abspath(sys.argv[1])
station_name = sys.argv[2]

station = extract_for_station(path, station_name)

print(f"Station found: {station.name}")
for direction, reading in station.readings.items():
    print(f"  {direction}: {len(reading.data)} samples, max = {reading.max_acc()}")
