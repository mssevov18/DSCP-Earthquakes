# nav_df.py
# Author: Martin Sevov
# -----------------------------------------------------------------------------
# "THE NAVDF-BEERWARE LICENSE" (Revision 1):
# As long as you retain this notice, you can do whatever you want with this file.
# If we meet someday and you think this stuff is useful, you can buy me a beer.
# The author gives no warranty and takes no responsibility for anything.
# -----------------------------------------------------------------------------

import pandas as pd
import os


def print_help():
    print(
        """--------------- ? Help Menu ? ---------------
[ commands ]
    q, Q -> quit/quit mode, absolute quit
    c -> clear last action
    r -> toggle NaN <-> \" \"
    R -> reset environment
    z -> turn on zoom mode (exit with q)
        'z' - \"interactive\" zoom
        'z rows_height columns_width' - skips the \"interaction\"
        'z rows_height columns_width row column' - previous but with coordinate move!
    Enter -> do the last non coordinate movement action
------------------------------------------------------
[ movement ]
    a/d -> left/right
    w/s -> up/down (only in zoom mode)
    column -> go to column position (only in non-zoom mode) [wraps around]
    row column -> go to row column position (only in zoom mode) [wraps around]
------------------------------------------------------
    At any point when writing coordinates or sizes (other than the regular movement)
    you can substitute the number with '-' for either same/default value.
------------------------------------------------------"""
    )


def clamp_within_range(a, mn, mx):
    if a >= mx:
        return a % mx
    if a < mn:
        return (mx - abs(a)) % mx
    return a


def split_num_parser(line, old_a, old_b, sep=" ", same="-"):
    a, b = 0, 0
    split = line.split(sep)
    if len(split) == 2:
        if split[0].isnumeric():
            a = int(split[0])
        elif split[0] == same:
            a = old_a
        else:
            raise ValueError(split[0])

        if split[1].isnumeric():
            b = int(split[1])
        elif split[1] == same:
            b = old_b
        else:
            raise ValueError(split[1])

    return a, b


def df_print(df, args=[], flags=None):
    rows = args[0]
    cols = args[1]
    row = args[2]
    col = args[3]
    width = args[4]
    height = args[5]

    subdf = None
    if flags["Zoomed"]:
        if height == -1:
            row = 0
            height = rows
        if width == -1:
            col = 0
            width = cols
        slice = df.iloc[row : row + height, col : col + width]
    else:
        slice = df.iloc[:rows, col]

    if flags["ReplaceNan"]:
        slice = slice.fillna("")

    os.system("cls" if os.name == "nt" else "clear")
    print(slice)


def nav_df(dataframe):
    if dataframe.empty:
        print("Empty Df")
        return

    rows, cols = dataframe.shape
    row, col = (0, 0)
    rh, cw = (5, 25)
    last_act = ""
    is_valid = True
    flags = {"Zoomed": False, "ReplaceNan": False}
    prompt = ""
    while True:
        # Clamp the head
        col = clamp_within_range(col, 0, cols)
        row = clamp_within_range(row, 0, rows)

        # If the movement option is not valid, clear last_act
        if not is_valid:
            last_act = ""
            is_valid = True

        # Show the head
        # print(dataframe.iloc[:rows, col])
        df_print(dataframe, [rows, cols, row, col, rh, cw], flags)

        # Update prompt and ask
        if flags["Zoomed"]:
            rcalc = row + rh
            ccalc = col + cw
            prompt = f"[{row}-{rows-1 if rcalc-rows > 0 else rcalc}]/{rows-1} [{col}-{cols-1 if ccalc-cols > 0 else ccalc}]/{cols-1} {"r " if flags["ReplaceNan"] else ""}'{last_act}' =|> "
        else:
            prompt = f"{rows-1}/{rows-1} {col}/{cols-1} {"r " if flags["ReplaceNan"] else ""}'{last_act}' |> "
        _in = input(prompt)

        # Perform base actions
        if _in == "":
            if last_act:
                _in = last_act
            else:
                col += 1
        else:
            match _in[0]:
                case "Q":
                    break
                case "q":
                    if flags["Zoomed"]:
                        flags["Zoomed"] = False
                        last_act = ""
                        continue
                    else:
                        break
                case "c":
                    last_act = ""
                    continue
                case "r":
                    flags["ReplaceNan"] = False if flags["ReplaceNan"] else True
                    continue
                case "R":
                    flags["Zoomed"] = False
                    flags["ReplaceNan"] = False
                    row = 0
                    col = 0
                    last_act = 0
                    is_valid = True
                    continue
                case "z":
                    sp = _in.split(" ")
                    if len(sp) == 3 or len(sp) == 5:
                        rh, cw = split_num_parser(sp[1] + " " + sp[2], rh, cw)
                        _in = _in[len(f"z {rh} {cw} ") :]
                    else:
                        result = input(
                            "Zooming with size col,rows (Enter for default; '-' for max; 'q' to stop; ['5 25']): "
                        )
                        if result == "":
                            rh, cw = (5, 25)
                        elif result == "q":
                            continue
                        else:
                            try:
                                rh, cw = split_num_parser(result, -1, -1)
                            except Exception:
                                rh, cw = (5, 25)
                    flags["Zoomed"] = True
                case "h":
                    print_help()
                    input("Enter to go back...")
                case "t":

                    print("Trim df to smaller size - no going back")
                    input()
                    raise NotImplementedError()

                case _:
                    last_act = _in

        # Move
        try:
            if _in != "" and (_in.isnumeric() or " " in _in or "-" in _in):
                if not flags["Zoomed"]:
                    # Jump to column
                    col = int(_in)
                else:
                    row, col = split_num_parser(_in, row, col)

                last_act = ""
                continue

            mem = ""
            i = 0
            while i < len(_in):
                if _in[i].isnumeric():  # Look at numbers for modifiers
                    nlen = 0
                    while i + 1 + nlen < len(_in) and _in[i + 1 + nlen].isnumeric():
                        nlen += 1
                    if nlen == 0:
                        mem = _in[i]
                    else:
                        mem = _in[i : nlen + 1]
                    i += len(mem)
                else:  # Perform the movement
                    num = 1
                    if mem != "":
                        num *= int(mem)
                    match _in[i]:
                        case "a":
                            col -= num
                        case "d":
                            col += num
                        case "w":
                            row -= num * flags["Zoomed"]
                        case "s":
                            row += num * flags["Zoomed"]
                        case _:
                            is_valid = False
                    i += 1

        except Exception as e:
            print(f"{e}")
            # print(f"'{e.message}' - [{e.args}]")
            input()
            last_act = ""

        finally:
            pass


if __name__ == "__main__":
    df = pd.DataFrame([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], columns=["a", "b", "c"])
    nav_df(df)
