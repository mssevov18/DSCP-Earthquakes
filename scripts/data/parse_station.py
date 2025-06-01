import os
import sys
import re
from .models import Station, StationReading


def is_station_file(filename, station_name):
    return filename.startswith(station_name) and re.match(
        r".+\.(EW|NS|UD)[12]?$", filename
    )


def parse_station_file(filepath):
    metadata = {}
    data = []
    in_data = False

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            if not line:
                continue

            if line.strip().startswith("Memo."):
                in_data = True
                metadata["Memo."] = ""
                continue

            if not in_data:
                # Use a fixed width for the key (17 chars), the rest is value
                key = line[:17].strip()
                val = line[17:].strip()

                # Normalize keys
                key = re.sub(r"\s+", " ", key).rstrip(".")

                # Clean up known value units
                if "Scale Factor" in key:
                    val = re.sub(r"\(.*?\)", "", val).strip()

                if "Sampling Freq" in key and "Hz" in val:
                    val = re.sub(r"[^\d.]", "", val)

                metadata[key] = val
                continue

            # Data line (after Memo.)
            try:
                numbers = list(map(int, line.split()))
                data.extend(numbers)
            except ValueError:
                continue

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
