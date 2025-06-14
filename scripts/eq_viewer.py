from scripts.data.models import Event, Station, StationReading
from scripts.data.extract import extract_event
from scripts.libs.interactive_lib import getch, clear, example_interactive_menu
from scripts.libs.nav_df import nav_df
from scripts.vis.multi_event_vis import *
import matplotlib.pyplot as plt
from typing import Union, List
import numpy as np
import pandas as pd


def enhanced_interactive_menu(
    static: str, options: list[str], max_visible: int = 10, item_prefix=""
) -> int:
    """
    Extended interactive menu:
    - Shows up to `max_visible` entries with scroll indicators
    - Navigate with W/S or ↑/↓
    - ENTER to select, Q to quit, F to filter
    """
    index = 0
    picked = -1
    filter_text = ""
    filtered = options.copy()
    box_width = 15

    while True:
        clear()
        print(static)
        if filter_text:
            print(f"Filter: {filter_text} (press F again to update)")

        total = len(filtered)
        if total == 0:
            print("[no matches]")
        else:
            start = max(0, index - max_visible // 2)
            end = min(total, start + max_visible)

            # Adjust window if near bottom
            if end - start < max_visible and start > 0:
                start = max(0, end - max_visible)

            # Show indicators
            if start > 0:
                print(f"┌{'─' * box_width}({start})┐\n")
            else:
                print(f"┌{'─' * box_width}───┐\n")

            # print(f"______/| {start} |\\______")

            for i in range(start, end):
                prefix = ">" if i == index else " "
                print(f"{prefix} {item_prefix}{filtered[i]}")

            if end < total:
                print(f"\n└{'─' * box_width}({end})┘")
            else:
                print(f"\n└{'─' * box_width}───┘")
            # print(f"‾‾‾‾‾‾\\| {total - end} |/‾‾‾‾‾‾")

        print("\nUse W/S or ↑/↓ to move, ENTER to select, Q to quit, F to filter")
        ch = getch()

        if ch in ["w", "\x1b[A"]:
            index = (index - 1) % total if total else 0
        elif ch in ["s", "\x1b[B"]:
            index = (index + 1) % total if total else 0
        elif ch in ["W"]:
            index = (index - 5) % total if total else 0
        elif ch in ["S"]:
            index = (index + 5) % total if total else 0
        elif ch.lower() == "f":
            filter_text = input("Enter filter text: ").strip()
            filtered = [o for o in options if filter_text.lower() in o.lower()]
            index = 0
        elif ch in ["\r", "\n"] and total:
            return options.index(filtered[index])
        elif ch.lower() == "q":
            return -1

    def select_many() -> list[int]:
        pass


def my_ui(
    static: str,
    options: list[(str, chr)],
    multiple=False,
    index=0,
    picked=-1,
    selected=[],
    filter_text="",
) -> Union[int, list[int]]:
    pass


def make_static(lines: List[str]):
    max_len = 4  # 4 is padding
    static = ""
    if type(lines) == str:
        max_len += len(lines)
        static = "| " + lines + (max_len - len(lines)) * " " + " |\n"
        lines = []
    elif type(lines) == list:
        max_len += max([len(line) for line in lines])
    else:
        return f"ERROR: Wrong type {type(lines)}"

    for line in lines:
        static += "| " + line + (max_len - len(line)) * " " + " |\n"

    return "/-" + max_len * "-" + "-\\\n" + static + "\\-" + max_len * "-" + "-/\n"


def view_events(events: list[Event]):
    static = make_static(
        [
            f"{len(events)} Event(s)",
        ]
    )
    event_labels = [f"[{e.magnitude}] {e.event_id} - <{e.origin_time}>" for e in events]
    event_labels.append("Plot magnitude frequencies")
    event_labels.append("Plot magnitudes over time")
    while True:
        choice = enhanced_interactive_menu(static, event_labels)
        nc = choice - len(events)
        if choice == -1:
            break
        if nc == 0:
            plot_magnitude_histogram(events)
        if nc == 1:
            plot_magnitude_timeline(events)
        elif nc < 0:
            event = events[choice]
            view_event(event)


def view_event(event: Event):
    static = make_static(
        [
            f"Event {event.event_id }",
            f"{event.num_kik_stations()} KIK stations",
            f"{event.num_knet_stations()} KNET stations",
            f"Time of origin: {event.origin_time}",
            f"Latitude: <{event.latitude}>",
            f"Longitude: <{event.longitude}>",
            f"Magnitude: {event.magnitude}",
        ]
    )
    station_names = list(event.stations.keys())

    while True:
        choice = enhanced_interactive_menu(
            static, station_names, item_prefix="Station "
        )
        if choice == -1:
            break  # user quit with 'q'
        station_name = station_names[choice]
        view_station(event.stations[station_name])


def view_station(station: Station):
    directions = station.directions()
    static = make_static(
        [
            f"Station Code: {station.name}",
            f"{station.type()} Station",
            f"Station Latitude: <{station.readings[directions[0]].station_lat}>",
            f"Station Longitude: <{station.readings[directions[0]].station_long}>",
            f"Station Height: <{station.readings[directions[0]].station_height}>",
        ]
    )

    while True:
        index = enhanced_interactive_menu(static, directions, item_prefix="Direction ")
        if index == -1:
            break  # user pressed 'q'
        direction = directions[index]
        reading = station.readings[direction]
        view_reading(reading)


def view_reading(reading: StationReading):
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

    if len(sys.argv) < 3:
        print("Usage: python eq_viewer <multi-event/event/station <ROOT_PATH>")
        sys.exit(1)

    if sys.argv[1] == "station":
        pass
    elif sys.argv[1] == "event":
        try:
            event = extract_event(sys.argv[2], sys.argv[2].split("/")[-1].strip())
        except:
            print("error......Consider adding logging // propper error handling")
            sys.exit(1)

        print(event)
        for name, station in event.stations.items():
            print(f"  {name}: {station.directions()}")

        # view_station(event.stations[list(event.stations.keys())[0]])
        view_event(event)
    elif sys.argv[1] == "multi-event":
        root_path = Path(sys.argv[2])
        if not root_path.exists() or not root_path.is_dir():
            print(f"Invalid root directory: {root_path}")
            sys.exit(1)

        events: list[Event] = []
        for child in sorted(root_path.iterdir()):
            if child.is_dir():
                try:
                    event = extract_event(str(child), child.name)
                    events.append(event)
                except Exception as e:
                    print(f"[!] Failed to load event from {child.name}: {e}")

        if not events:
            print("No valid events found.")
            sys.exit(1)

        view_events(events)

    else:
        print(f"Wrong target group: {sys.argv[1]}...\nmulti-event / event / station")
