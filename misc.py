import json


def load_language(lang=None):
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
            lang = json.load(open("resources/settings.json", "r"))["language"]
        with open(f"resources/languages/{lang}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        f.close()
    except FileNotFoundError:
        data = None
    return data
