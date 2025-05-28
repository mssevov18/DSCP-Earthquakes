from typing import Optional, List, Dict
from dataclasses import dataclass, field
import pandas as pd
import re


class StationReading:
    def __init__(
        self,
        origin_time: Optional[str],
        latitude: Optional[float],
        longitude: Optional[float],
        depth_km: Optional[float],
        magnitude: Optional[float],
        station_code: Optional[str],
        station_lat: Optional[float],
        station_long: Optional[float],
        station_height: Optional[float],
        record_time: Optional[str],
        sampling_freq_hz: Optional[float],
        duration_s: Optional[float],
        direction: Optional[str],
        scale_factor: Optional[str],  # raw string for now
        max_acc_gal: Optional[float],
        last_correction: Optional[str],
        memo: Optional[str],
        data: list[int],
    ):
        self.origin_time = origin_time
        self.latitude = latitude
        self.longitude = longitude
        self.depth_km = depth_km
        self.magnitude = magnitude
        self.station_code = station_code
        self.station_lat = station_lat
        self.station_long = station_long
        self.station_height = station_height
        self.record_time = record_time
        self.sampling_freq_hz = sampling_freq_hz
        self.duration_s = duration_s
        self.direction = direction
        self.scale_factor = scale_factor
        self.max_acc_gal = max_acc_gal
        self.last_correction = last_correction
        self.memo = memo
        self.data = data
        self._cached_df: Optional[pd.DataFrame] = None

    def to_dataframe(
        self, with_time: bool = True, apply_scale: bool = True, use_cache: bool = True
    ) -> pd.DataFrame:
        if self._cached_df is not None and use_cache:
            return self._cached_df

        try:
            scale = (
                float(self.scale_factor) if apply_scale and self.scale_factor else 1.0
            )
        except ValueError:
            scale = 0

        df = pd.DataFrame({"acc": [x * scale for x in self.data]})

        if with_time and self.sampling_freq_hz:
            dt = 1.0 / self.sampling_freq_hz
            df["time_s"] = df.index * dt

        self._cached_df = df
        return df

    def invalidate_cache(self):
        self._cached_df = None

    @classmethod
    def from_dict(cls, metadata: dict[str, str], data: list[int]) -> "StationReading":
        print("Available metadata keys:", list(metadata.keys()))

        def try_parse_float(key):
            try:
                return float(metadata.get(key)) if key in metadata else None
            except ValueError:
                return None

        def try_parse_str(key):
            return metadata.get(key, None)

        def parse_scale_factor(raw: str) -> str:
            """
            Converts strings like '3923(gal)/8224838' to a float string.
            Falls back to the raw string if parsing fails.
            """
            if raw:
                try:
                    
                    numerator, denominator = re.sub(r"[(]gal[)]/.*", "", raw), re.sub(r".*/", "", raw)
                    scale = float(numerator.strip()) / float(denominator.strip())
                    return str(scale)
                except Exception:
                    pass
            return raw

        scale_raw = try_parse_str("Scale Factor")
        parsed_scale = parse_scale_factor(scale_raw)

        return cls(
            origin_time=try_parse_str("Origin Time"),
            latitude=try_parse_float("Lat."),
            longitude=try_parse_float("Long."),
            depth_km=try_parse_float("Depth. (km)"),
            magnitude=try_parse_float("Mag."),
            station_code=try_parse_str("Station Code"),
            station_lat=try_parse_float("Station Lat."),
            station_long=try_parse_float("Station Long."),
            station_height=try_parse_float("Station Height(m)"),
            record_time=try_parse_str("Record Time"),
            sampling_freq_hz=try_parse_float("Sampling Freq(Hz)"),
            duration_s=try_parse_float("Duration Time(s)"),
            direction=try_parse_str("Dir."),
            scale_factor=parsed_scale,
            max_acc_gal=try_parse_float("Max. Acc. (gal)"),
            last_correction=try_parse_str("Last Correction"),
            memo=try_parse_str("Memo."),
            data=data,
        )

    def max_acc(self):
        return max(self.data) if self.data else None

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"<Reading len={len(self.data)}, max={self.max_acc()}>"


class Station:
    def __init__(self, name: str):
        self.name = name
        self.readings: dict[str, StationReading] = {}

    def add_reading(self, direction: str, reading: StationReading):
        self.readings[direction] = reading

    def directions(self):
        return list(self.readings.keys())

    def __repr__(self):
        return f"<Station {self.name} with directions: {self.directions()}>"


@dataclass
class Event:
    event_id: str
    stations: dict[str, Station] = field(default_factory=dict)

    origin_time: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    depth_km: Optional[float] = None
    magnitude: Optional[float] = None

    def add_station(self, station: Station):
        self.stations[station.name] = station

    def num_stations(self) -> int:
        return len(self.stations)

    def __repr__(self):
        return f"<Event {self.event_id} | {len(self.stations)} stations>"
