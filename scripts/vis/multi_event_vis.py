#!/usr/bin/env python3

from scripts.data.models import Event, Station, StationReading
import matplotlib.pyplot as plt


def plot_magnitude_histogram(events: list[Event]):
    magnitudes = [e.magnitude for e in events if e.magnitude is not None]

    if not magnitudes:
        print("[!] No magnitudes to plot.")
        return

    plt.figure(figsize=(8, 4))
    plt.hist(magnitudes, bins=10, edgecolor="black")
    plt.xlabel("Magnitude")
    plt.ylabel("Frequency")
    plt.title("Histogram of Earthquake Magnitudes")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_magnitude_timeline(events: list[Event]):
    # Filter and sort by time
    valid_events = [
        e for e in events if e.magnitude is not None and e.origin_time is not None
    ]
    if not valid_events:
        print("[!] No events with both magnitude and time.")
        return

    # Sort chronologically
    valid_events.sort(key=lambda e: e.origin_time)
    times = [e.origin_time for e in valid_events]
    magnitudes = [e.magnitude for e in valid_events]

    plt.figure(figsize=(10, 3))
    plt.plot(times, magnitudes, marker="o", linestyle="-", linewidth=1)
    plt.xlabel("Time")
    plt.ylabel("Magnitude")
    plt.title("Earthquake Magnitudes Over Time")
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.show()
