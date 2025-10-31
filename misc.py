import json


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
        with open(f"resources/languages/{lang}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        f.close()
    except FileNotFoundError:
        data = None
    return data


def load_settings():
    with open("resources/settings.json", "r") as f:
        data = json.load(f)
    f.close()
    return data
