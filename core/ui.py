#!/usr/bin/env python3

import os
import sys
import platform
from .core import Color, get_target, clear_screen

# ============================================================
# ASCII MENU (Works everywhere)
# ============================================================
def ascii_menu(options, title="MENU", show_back=True):
    """
    Simple ASCII menu that works in all environments
    Returns: selected option number as string
    """
    clear_screen()  # این صفحه رو پاک میکنه
    
    # Print title
    print(Color.BC + "╔" + "═" * 50 + "╗")
    print(f"║{Color.BG}{title:^50}{Color.BC}║")
    print("╚" + "═" * 50 + "╝" + Color.N)
    print()
    
    # Print options
    for i, option in enumerate(options, 1):
        if "Back" in option or "Exit" in option:
            print(f"{Color.Y}[{i}] {option}{Color.N}")
        else:
            print(f"{Color.C}[{i}] {option}{Color.N}")
    
    if show_back:
        print(f"\n{Color.Y}[B] Back{Color.N}")
    print(f"{Color.R}[Q] Quit{Color.N}")
    
    # Get user choice
    while True:
        try:
            choice = input(f"\n{Color.G}└─➤ {Color.N}").strip().upper()
            
            if choice == 'Q':
                sys.exit(0)
            elif show_back and choice == 'B':
                return 'B'
            elif choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(options):
                    return str(num)
            
            print(f"{Color.R}[!] Invalid choice{Color.N}")
        except KeyboardInterrupt:
            print(f"\n{Color.Y}[*] Exiting...{Color.N}")
            sys.exit(0)
        except:
            print(f"{Color.R}[!] Error{Color.N}")


# ============================================================
# ULTRA MENU (Fancy version with colors)
# ============================================================
def ultra_menu(options, title="ULTRA MENU", show_back=True):
    """
    Fancy menu with better formatting
    Returns: selected option number as string
    """
    clear_screen()  # این صفحه رو پاک میکنه
    
    # Print fancy header
    print(Color.BC + "╔" + "═" * 60 + "╗")
    print(f"║{Color.BM}{title:^60}{Color.BC}║")
    print("╠" + "═" * 60 + "╣")
    
    # Current target if set
    target = get_target()
    if target:
        print(f"║ {Color.G}[✓] Target:{Color.Y} {target:<47}{Color.BC} ║")
        print("╠" + "═" * 60 + "╣")
    
    print("╚" + "═" * 60 + "╝" + Color.N)
    print()
    
    # Print options in columns if enough options
    if len(options) > 10:
        # Two columns
        mid = len(options) // 2 + len(options) % 2
        for i in range(mid):
            left_idx = i
            right_idx = i + mid
            
            left_num = f"[{left_idx+1}]"
            left_text = options[left_idx][:25]
            
            if right_idx < len(options):
                right_num = f"[{right_idx+1}]"
                right_text = options[right_idx][:25]
                print(f"{Color.C}{left_num:<5} {left_text:<25} {Color.C}{right_num:<5} {right_text:<25}{Color.N}")
            else:
                print(f"{Color.C}{left_num:<5} {left_text:<25}{Color.N}")
    else:
        # Single column
        for i, option in enumerate(options, 1):
            if "Back" in option or "Exit" in option:
                print(f"{Color.Y}[{i}] {option}{Color.N}")
            else:
                print(f"{Color.C}[{i}] {option}{Color.N}")
    
    if show_back:
        print(f"\n{Color.Y}[B] Back to Main Menu{Color.N}")
    print(f"{Color.R}[Q] Quit Framework{Color.N}")
    
    # Get user choice
    while True:
        try:
            choice = input(f"\n{Color.G}└─➤ {Color.N}").strip().upper()
            
            if choice == 'Q':
                print(f"\n{Color.Y}[*] Goodbye!{Color.N}")
                sys.exit(0)
            elif show_back and choice == 'B':
                return 'B'
            elif choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(options):
                    return str(num)
            
            print(f"{Color.R}[!] Invalid choice{Color.N}")
        except KeyboardInterrupt:
            print(f"\n{Color.Y}[*] Exiting...{Color.N}")
            sys.exit(0)


# ============================================================
# LOAD/SAVE MENU MODE
# ============================================================
MENU_MODE_FILE = "menu_mode.txt"

def save_mode(mode):
    """Save menu mode (ascii/ultra)"""
    try:
        with open(MENU_MODE_FILE, "w") as f:
            f.write(mode)
    except:
        pass

def load_mode():
    """Load menu mode"""
    try:
        if os.path.exists(MENU_MODE_FILE):
            with open(MENU_MODE_FILE, "r") as f:
                return f.read().strip()
    except:
        pass
    return "ultra"  # Default mode


# ============================================================
# INPUT WITH VALIDATION
# ============================================================
def get_input(prompt, validator=None, default=None):
    """
    Get user input with validation
    """
    while True:
        try:
            value = input(f"{Color.G}{prompt}{Color.N}").strip()
            
            if not value and default is not None:
                return default
            
            if validator:
                if validator(value):
                    return value
                else:
                    print(f"{Color.R}[!] Invalid input{Color.N}")
            else:
                return value
                
        except KeyboardInterrupt:
            print(f"\n{Color.Y}[*] Cancelled{Color.N}")
            return None
        except:
            print(f"{Color.R}[!] Error{Color.N}")


# ============================================================
# YES/NO PROMPT
# ============================================================
def confirm(prompt, default=True):
    """
    Yes/No confirmation prompt
    """
    suffix = " [Y/n] " if default else " [y/N] "
    
    while True:
        try:
            choice = input(f"{Color.Y}{prompt}{suffix}{Color.N}").strip().upper()
            
            if not choice:
                return default
            if choice in ['Y', 'YES']:
                return True
            if choice in ['N', 'NO']:
                return False
            
            print(f"{Color.R}[!] Please answer Y or N{Color.N}")
        except KeyboardInterrupt:
            print(f"\n{Color.Y}[*] Cancelled{Color.N}")
            return False


# ============================================================
# PROGRESS BAR
# ============================================================
def progress_bar(current, total, bar_length=40):
    """
    Display a progress bar
    """
    percent = float(current) * 100 / total
    arrow = '-' * int(percent/100 * bar_length - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    
    sys.stdout.write(f"\r{Color.C}[{arrow}{spaces}] {percent:.1f}%{Color.N}")
    sys.stdout.flush()


# ============================================================
# SELECT FROM LIST
# ============================================================
def select_from_list(items, title="Select an item"):
    """
    Let user select an item from a list
    Returns: selected item or None
    """
    if not items:
        print(f"{Color.Y}[!] No items to select{Color.N}")
        return None
    
    print(f"\n{Color.BC}{title}{Color.N}\n")
    
    for i, item in enumerate(items, 1):
        print(f"{Color.C}[{i}] {item}{Color.N}")
    
    print(f"\n{Color.Y}[0] Cancel{Color.N}")
    
    while True:
        try:
            choice = input(f"\n{Color.G}Select: {Color.N}").strip()
            
            if choice == '0':
                return None
            if choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(items):
                    return items[num-1]
            
            print(f"{Color.R}[!] Invalid choice{Color.N}")
        except KeyboardInterrupt:
            print()
            return None