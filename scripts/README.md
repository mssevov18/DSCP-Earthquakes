# Earthquake Station Data Extractor

---

## 📦 Models (`models.py`)

### `Station`
- Represents a single seismic station (e.g. `HDKH01`)
- Holds readings in a dict: `readings: Dict[str, StationReading]`
- Methods:
  - `add_reading(direction: str, reading: StationReading)`
  - `directions() → List[str]`

### `StationReading`
- Contains:
  - Explicit metadata fields (origin time, lat/lon, etc.)
  - `data: List[int]` – numeric waveform values
- Created via `StationReading.from_dict(metadata: dict, data: list)`
- Methods:
  - `max_acc()` → max acceleration in `data`
  - `__len__()` for sample count

---

## 🧪 Parser (`parse_station.py`)

- Main logic to walk a directory and extract data for a given station.
- Filters station files by name and direction (EW/NS/UD + optional 1/2).
- Uses `.from_dict()` to construct `StationReading` objects.

### Key Functions
- `is_station_file(filename, station_name)`
- `parse_station_file(filepath)` – parses metadata + waveform
- `extract_for_station(path, station_name) → Station`

---

## 🚀 Example CLI (`example_find.py`)

```sh
python example_find.py <PATH> <STATION_NAME>

```
