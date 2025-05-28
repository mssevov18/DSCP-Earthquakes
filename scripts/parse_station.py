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
    in_data = False

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Switch to data mode after "Memo." line
            if line.strip().startswith("Memo."):
                in_data = True
                metadata["Memo."] = ""  # explicitly include the key
                continue

            if not in_data:
                # Split on two or more spaces
                parts = re.split(r"\s{2,}", line, maxsplit=1)
                if len(parts) == 2:
                    key, val = parts[0].strip(), parts[1].strip()

                    # Handle Scale Factor cleanup
                    if key == "Scale Factor":
                        val = re.sub(r"\(.*?\)", "", val).strip()

                    # Handle Sampling Freq(Hz): remove "Hz"
                    if key == "Sampling Freq(Hz)":
                        val = re.sub(r"[^\d.]", "", val)

                    metadata[key] = val
                continue

            # If in_data: read numeric values
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
