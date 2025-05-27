---
title: Earthquake Station Data Extractor
---

## 🧠 Project Overview

Extract and organize seismic station waveform data from earthquake records.

- Parses `.EW`, `.NS`, `.UD` files from `kik/` and `knt/` folders
- Captures structured metadata + wave data
- Typed Python models using no external libraries
- Supports per-station directional readings

Main files:
- `models.py` — object structure
- `parse_station.py` — main logic
- `example_find.py` — CLI demo tool

<!-- end_slide -->

## 🧩 models.py — StationReading

Represents a single waveform recording for a station in a direction (e.g., `NS1`).

### Fields:
- `origin_time: Optional[str]`
- `latitude, longitude, depth_km: Optional[float]`
- `magnitude: Optional[float]`
- `station_code, record_time, direction: Optional[str]`
- `station_lat, station_long, station_height: Optional[float]`
- `sampling_freq_hz, duration_s, max_acc_gal: Optional[float]`
- `scale_factor, memo, last_correction: Optional[str]`
- `data: list[int]` — wave values

### Methods:
- `from_dict(metadata: dict, data: list) → StationReading`
- `max_acc()` → max wave value
- `__len__()` → number of samples

<!-- end_slide -->

## 🧩 models.py — Station

Represents a single seismic station across directions.

### Fields:
- `name: str`
- `readings: dict[str, StationReading]`

### Methods:
- `add_reading(direction: str, reading: StationReading)`
- `directions() → list[str]`
- `__repr__()` → summary output

<!-- end_slide -->

## 🛠️ parse_station.py

Main logic to load `.EW`, `.NS`, `.UD` files for a specific station.

### Key functions:
- `is_station_file(filename, station_name)`
- `parse_station_file(filepath)`
  - Reads metadata until `Last Correction`
  - Then extracts numeric wave values
- `extract_for_station(path, station_name) → Station`

If run directly:
```sh
python parse_station.py STATION_NAME
```

Scans from the current directory.

<!-- end_slide -->

## 🚀 example_find.py

Simple script to test the system end-to-end.

Usage:
```sh
python example_find.py <PATH> <STATION_NAME>
```

- Loads the dataset under `<PATH>`
- Extracts and prints summary for `<STATION_NAME>`:
  - Available directions
  - Number of samples
  - Max acceleration


