# Settings.py
from core.ui import load_mode, save_mode, ascii_menu, ultra_menu
from core.core import Color
import os

def clear():
    os.system("cls" if os.name == "nt" else "clear")

OPTIONS = [
    "Switch to ASCII Menu",
    "Switch to Ultra UI Menu",
    "Back"
]

def settings_menu():
    while True:
        clear()
        print(Color.C + "Settings\n" + Color.N)
        print(f"Current Menu Mode: {load_mode()}\n")

        mode = load_mode()

        # Always use ASCII in PyCharm
        if "PYCHARM_HOSTED" in os.environ:
            choice = ascii_menu(OPTIONS)
        else:
            if mode == "ascii":
                choice = ascii_menu(OPTIONS)
            else:
                choice = ultra_menu(OPTIONS)

        if choice == "1":
            save_mode("ascii")
            print(Color.G + "Switched to ASCII mode." + Color.N)
            input("Press ENTER...")

        elif choice == "2":
            save_mode("ultra")
            print(Color.G + "Switched to Ultra UI mode." + Color.N)
            input("Press ENTER...")

        elif choice == "3":
            return
