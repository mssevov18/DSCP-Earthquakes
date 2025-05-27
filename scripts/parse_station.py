import os
import sys
import re
from models import Station, StationReading


def is_station_file(filename, station_name):
    return filename.startswith(station_name) and re.match(
        r".+\.(EW|NS|UD)[12]?$", filename
    )


def parse_station_file(filepath):
    metadata = {}
    data = []
    with open(filepath, "r") as f:
        in_data = False
        for line in f:
            line = line.strip()
            if not in_data:
                if line.startswith("Last Correction"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        metadata[key.strip()] = val.strip()
                    in_data = True
                    continue
                elif ":" in line:
                    key, val = line.split(":", 1)
                    metadata[key.strip()] = val.strip()
                continue
            if in_data:
                try:
                    numbers = list(map(int, line.split()))
                    data.extend(numbers)
                except ValueError:
                    pass  # Ignore bad lines
    return metadata, data


def extract_for_station(path, station_name):
    station = Station(station_name)
    for subdir, _, files in os.walk(path):
        for file in files:
            if is_station_file(file, station_name):
                full_path = os.path.join(subdir, file)
                try:
                    direction = file.split(".")[-1]
                    metadata, data = parse_station_file(full_path)
                    reading = StationReading.from_dict(metadata, data)
                    station.add_reading(direction, reading)
                except Exception as e:
                    print(f"Failed to parse {file}: {e}")
    return station


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_station.py <STATION_NAME>")
        sys.exit(1)

    cwd = os.getcwd()
    station_name = sys.argv[1]
    station = extract_for_station(cwd, station_name)
    print(station)
