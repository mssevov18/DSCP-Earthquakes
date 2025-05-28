import os
import sys

# Platform-specific imports for keypress
if os.name == "nt":
    import msvcrt
else:
    import tty
    import termios


# Get a single character (no Enter)
def getch():
    if os.name == "nt":
        return msvcrt.getch().decode()
    else:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


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
