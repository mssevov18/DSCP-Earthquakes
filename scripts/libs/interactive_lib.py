import os
import sys

# Platform-specific imports for keypress
if os.name == "nt":
    import msvcrt
else:
    import tty
    import termios


import os
import sys

def getch():
    if os.name == "nt":
        import msvcrt
        first = msvcrt.getch()
        if first in {b'\x00', b'\xe0'}:
            second = msvcrt.getch()
            win_to_linux_escape = {
                b'H': '\x1b[A',  # Up arrow
                b'P': '\x1b[B',  # Down arrow
                b'M': '\x1b[C',  # Right arrow
                b'K': '\x1b[D'   # Left arrow
            }
            return win_to_linux_escape.get(second, '')
        else:
            return first.decode(errors='ignore')
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# Clear screen (cross-platform)
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def example_interactive_menu(static, options):
    index = 0
    picked = -1
    while True:
        clear()
        print(static)
        for i, opt in enumerate(options):
            if i == index:
                print(f"> {opt}")
            else:
                print(f"  {opt}")

        print("\nUse W/S or ↑/↓ to move, Q to quit")
        ch = getch()
        if ch in ["w", "\x1b[A"]:  # 'w' or Up arrow
            index = (index - 1) % len(options)
        elif ch in ["s", "\x1b[B"]:  # 's' or Down arrow
            index = (index + 1) % len(options)
        elif ch in ["\r", "\n"]:
            return index
        elif ch.lower() == "q":
            break


# Example usage
if __name__ == "__main__":
    options = ["Start", "Settings", "About", "Exit"]
    interactive_menu("", options)
