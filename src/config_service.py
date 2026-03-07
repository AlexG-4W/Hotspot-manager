import winreg
import sys
import logging

APP_NAME = "Windows Mobile Hotspot Manager"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

def check_autostart() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return value == sys.argv[0]
    except FileNotFoundError:
        return False
    except Exception as e:
        logging.error(f"Error checking autostart: {e}")
        return False

def set_autostart(enable: bool):
    try:
        if enable:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, sys.argv[0])
            winreg.CloseKey(key)
            logging.info("Autostart enabled.")
        else:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, APP_NAME)
            winreg.CloseKey(key)
            logging.info("Autostart disabled.")
    except Exception as e:
        logging.error(f"Error configuring autostart: {e}")