from scripts.data.models import Event, Station, StationReading
from scripts.data.extract import extract_event
from scripts.libs.interactive_lib import getch, clear, example_interactive_menu
from scripts.libs.nav_df import nav_df
import matplotlib.pyplot as plt


def enhanced_interactive_menu(static: str, options: list[str]) -> int:
    """
    Extended interactive menu:
    - Navigate with W/S or ↑/↓
    - Press ENTER to select
    - Press Q to cancel and return -1
    - Press F to enter filter mode
    """
    index = 0
    picked = -1
    filter_text = ""
    filtered = options.copy()

    while True:
        clear()
        print(static)
        if filter_text:
            print(f"Filter: {filter_text} (press F again to update)")
        for i, opt in enumerate(filtered):
            prefix = ">" if i == index else " "
            print(f"{prefix} {opt}")

        print("\nUse W/S or ↑/↓ to move, ENTER to select, Q to quit, F to filter")
        ch = getch()

        if ch in ["w", "\x1b[A"]:
            index = (index - 1) % len(filtered)
        elif ch in ["s", "\x1b[B"]:
            index = (index + 1) % len(filtered)
        elif ch.lower() == "f":
            # clear()
            # print(static)
            filter_text = input("Enter filter text: ").strip()
            filtered = [o for o in options if filter_text.lower() in o.lower()]
            index = 0
        elif ch in ["\r", "\n"]:
            return options.index(filtered[index])
        elif ch.lower() == "q":
            return -1


def view_event(event: Event):
    static = f"<Event {event.event_id } | {len(event.stations)} stations>"
    station_names = list(event.stations.keys())

    while True:
        choice = enhanced_interactive_menu(static, station_names)
        if choice == -1:
            break  # user quit with 'q'
        station_name = station_names[choice]
        view_station(event.stations[station_name])


def view_station(station: Station):
    static = f"Station Code: {station.name}"
    directions = station.directions()

    while True:
        index = enhanced_interactive_menu(static, directions)
        if index == -1:
            break  # user pressed 'q'
        direction = directions[index]
        reading = station.readings[direction]
        view_reading(reading)


def view_reading(reading: StationReading):
    import pandas as pd

    df = reading.to_dataframe()
    options = ["Show plot", "Show nav_df", "Describe stats", "Back"]

    static = (
        f"<Reading | Station: {reading.station_code} | Dir: {reading.direction}>\n"
        f"Samples: {len(reading.data)}, Scale factor: {reading.scale_factor}"
    )

    while True:
        choice = enhanced_interactive_menu(static, options)

        if choice == -1 or options[choice] == "Back":
            break
        elif options[choice] == "Show plot":
            plot_reading(reading)
        elif options[choice] == "Show nav_df":
            nav_df(df)
        elif options[choice] == "Describe stats":
            print(df.describe())
            input("\nPress Enter to continue...")


import matplotlib.pyplot as plt
import numpy as np


def plot_reading(reading: StationReading):
    if not reading.data or len(reading.data) == 0:
        print("[!] No data to plot.")
        return
    if reading.sampling_freq_hz is None:
        print("[!] Sampling frequency is missing.")
        return
    if not reading.scale_factor:
        print("[!] Scale factor is missing.")
        return
    try:
        scale = float(reading.scale_factor)
    except ValueError:
        print(f"[!] Invalid scale factor: {reading.scale_factor}")
        return

    time_s = np.arange(len(reading.data)) / reading.sampling_freq_hz
    acc = np.array(reading.data) * scale

    plt.figure(figsize=(10, 4))
    plt.plot(time_s, acc, label=f"{reading.direction}")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (gal)")
    plt.title(f"{reading.station_code} - {reading.direction}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python eq_viewer <ROOT_PATH>")
        sys.exit(1)

    try:
        event = extract_event(sys.argv[1], sys.argv[1].split("/")[-1].strip())
    except:
        print("error......Consider adding logging // propper error handling")
        sys.exit(1)

    print(event)
    for name, station in event.stations.items():
        print(f"  {name}: {station.directions()}")

    # view_station(event.stations[list(event.stations.keys())[0]])
    view_event(event)
