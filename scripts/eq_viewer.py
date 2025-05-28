from models import Event, Station, StationReading
from extract_event import extract_event, extract_all_stations
from interactive_lib import getch, clear, example_interactive_menu
from nav_df import nav_df


def view_event():
    pass


def view_station(station: Station):
    input()
    static = f"Station Code: {station.name}"
    index = example_interactive_menu(static, station.directions())
    if index <= len(station.directions()) and index >= 0:
        view_reading(station.readings[station.directions()[index]])


def view_reading(reading: StationReading):
    print(reading)
    print(reading.scale_factor)
    print(len(reading.data))
    df = reading.to_dataframe()
    inp = input("nav_df? y/n: ")
    if inp in ["y", "Y"]:
        nav_df(df)
    else:
        print(df.describe())
    nav_df(reading.to_dataframe(False, False, False))


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

    view_station(event.stations[list(event.stations.keys())[0]])
