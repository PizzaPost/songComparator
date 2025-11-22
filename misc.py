import ctypes
import json
import os


def load_language(settings, lang=None):
    """loads the language file

    Parameters
    ----------
    lang : str (optional: default is set in settings.json and fallback to english)
        The language to load.

    Returns
    -------
    dict
        The translations for the given language.

    or

    None
        If no specified language is found.
    """
    try:
        if lang is None:
            lang = settings["language"]
        with open(os.path.join("resources", "languages", f"{lang}.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        f.close()
    except FileNotFoundError:
        data = None
    return data


def load_settings():
    with open(os.path.join("resources", "settings.json"), "r") as f:
        data = json.load(f)
    f.close()
    return data


def isLogEnabled():
    settings_json = load_settings()
    return settings_json["logging"]

def get_current_os():
    return os.name

def hide_file(file):
    """Hides a file or directory using OS-specific methods."""
    current_os=get_current_os()
    if current_os == "Windows":
        ctypes.windll.kernel32.SetFileAttributesW(file, 0x02)
    elif current_os == "Darwin":
        os.system(f'chflags hidden "{file}"')

def unhide_file(file):
    """Unhides a file or directory using OS-specific methods."""
    current_os=get_current_os()
    if current_os == "Windows":
        ctypes.windll.kernel32.SetFileAttributesW(file, 0x80)
    elif current_os == "Darwin":
        os.system(f'chflags nohidden "{file}"')
