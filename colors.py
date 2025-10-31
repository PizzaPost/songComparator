import json
import os
import urllib
from tkinter import ttk





def load_palette(filename="resources/themes/default.json"):
    """Loads the palette from a JSON file.
    Returns a flat palette dict for classic tkinter use.
    Also ensures the file contains a customtkinter-compatible CTk theme.
    """
    default = {
        "background": "#0b0d0f",
        "bg": "#0f1113",
        "text": "#e6e6e6",
        "dark_red": "#7C0008",
        "light_red": "#EA5660",
        "button_bg": "#1a1c1e",
        "button_fg": "#f3f4f5",
        "button_active_bg": "#EA5660",
        "button_disabled_color": "#999999",
        "border": "#232629",
        "progress_trough": "#151718",
        "progress_bar": "#7C0008",
        "hover_red": "#a33c43",
    }

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = None
    else:
        data = None

    if data is None:
        # download file with both "palette" and CTk theme
        link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/resources/themes/default.json"
        urllib.request.urlretrieve(link, f"resources/themes/{default}.json")
        ctk=json.load(open(f"resources/themes/{default}.json", "r", encoding="utf-8"))
        # store palette under "palette" key and also the CTk theme keys
        out = {"palette": default}
        out.update(ctk)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        return default

    # if the file contains a "palette" key, use it.
    if isinstance(data, dict) and "palette" in data and isinstance(data["palette"], dict):
        palette = {**default, **data["palette"]}
        # ensure file also contains CTk fields or adds them
        missing_ctk = any(k.startswith("CTk") or k == "CTk" for k in data.keys())
        if not missing_ctk:
            link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/resources/themes/default.json"
            urllib.request.urlretrieve(link, f"resources/themes/{default}.json")
            ctk = json.load(open(f"resources/themes/{default}.json", "r", encoding="utf-8"))
            data.update(ctk)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        return palette

    # if the file looks like a CTk theme (top-level CTk keys), extract a palette
    # we only extract colors that exist in the file; otherwise fall back to default.
    if isinstance(data, dict):
        try:
            # helper to get the first color
            def get(k, subk, idx=0):
                "Get the first color from a CTk theme dictionary."
                v = data.get(k, {}).get(subk)
                if isinstance(v, list) and len(v) > idx:
                    return v[idx]
                if isinstance(v, str):
                    return v
                return None

            palette = {
                "background": get("CTk", "fg_color", 1) or get("CTkToplevel", "fg_color", 1) or default["background"],
                "bg": get("CTk", "fg_color", 0) or get("CTkFrame", "fg_color", 0) or default["bg"],
                "text": get("CTkLabel", "text_color", 0) or get("CTkButton", "text_color", 0) or default["text"],
                "dark_red": default["dark_red"],
                "light_red": default["light_red"],
                "button_bg": get("CTkButton", "fg_color", 0) or default["button_bg"],
                "button_fg": get("CTkButton", "text_color", 0) or get("CTkLabel", "text_color", 0) or default[
                    "button_fg"],
                "button_active_bg": get("CTkButton", "fg_color", 1) or default["button_active_bg"],
                "border": get("CTkFrame", "border_color", 0) or default["border"],
                "progress_trough": get("CTkProgressBar", "fg_color", 0) or default["progress_trough"],
                "progress_bar": get("CTkProgressBar", "progress_color", 0) or default["progress_bar"],
                "hover_red": get("CTkButton", "hover_color", 0) or default["hover_red"],
            }
            # fill any None with defaults
            for k in default:
                if not palette.get(k):
                    palette[k] = default[k]
            # ensure the file contains "palette" key so future reads are easier
            if "palette" not in data:
                data["palette"] = palette
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            return palette
        except Exception:
            return default

    return default


def bind_hover_classic_button(btn, palette):
    """Adds a hover style for classic tkinter Buttons."""
    if getattr(btn, "_hover_bound", False):
        return
    btn._hover_bound = True
    try:
        btn._orig_bg = btn.cget("bg")
        btn._orig_fg = btn.cget("fg")
        btn._orig_active = btn.cget("activebackground")
    except Exception:
        btn._orig_bg, btn._orig_fg, btn._orig_active = palette["button_bg"], palette["button_fg"], palette[
            "button_active_bg"]

    def on_enter(e):
        try:
            btn.configure(bg=palette["hover_red"], fg=palette["button_fg"],
                          activebackground=palette["button_active_bg"])
        except Exception:
            pass

    def on_leave(e):
        try:
            btn.configure(bg=btn._orig_bg, fg=btn._orig_fg,
                          activebackground=btn._orig_active or palette["button_active_bg"])
        except Exception:
            pass

    btn.bind("<Enter>", on_enter, add="+")
    btn.bind("<Leave>", on_leave, add="+")

    try:
        btn.configure(
            bg=palette["button_bg"],
            fg=palette["button_fg"],
            activebackground=palette["button_active_bg"],
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            highlightthickness=0,
            padx=8,
            pady=4,
            disabledforeground=palette.get("text", "gray60")
        )
    except Exception:
        pass


def set_color(widget, palette):
    """Apply an "aqua" themed dark mode to classic tkinter widgets. (Sadly only works on macOS.)"""
    style = ttk.Style()
    for theme_try in ("aqua", "arc", "breeze", "yaru", "default"):
        try:
            style.theme_use(theme_try)
            break
        except Exception:
            continue

    style.configure("Aqua.Dark.TFrame", background=palette["bg"])
    style.configure("Aqua.Dark.TLabel", background=palette["bg"], foreground=palette["text"])
    style.configure("Aqua.Dark.TButton",
                    background=palette["button_bg"],
                    foreground=palette["button_fg"],
                    relief="flat",
                    padding=(8, 4))
    style.map("Aqua.Dark.TButton",
              background=[("active", palette["hover_red"]), ("pressed", palette["button_active_bg"])],
              foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
    style.configure("Aqua.Horizontal.TProgressbar",
                    troughcolor=palette["progress_trough"],
                    background=palette["progress_bar"],
                    bordercolor=palette["border"])

    cls = widget.__class__.__name__

    if cls in ("Tk", "Toplevel"):
        try:
            widget.configure(bg=palette["background"])
        except Exception:
            pass

    if cls in ("Frame", "LabelFrame"):
        try:
            widget.configure(bg=palette["bg"], bd=0, highlightthickness=0)
        except Exception:
            pass

    if cls == "Label":
        try:
            widget.configure(bg=palette["bg"], fg=palette["text"])
        except Exception:
            pass

    if cls == "Button":
        try:
            # base + active + hover handled by bind_hover_classic_button
            btn_kwargs = dict(
                bg=palette["button_bg"],
                fg=palette["button_fg"],
                activebackground=palette["button_active_bg"],
                activeforeground="#ffffff",
                bd=0, relief="flat", padx=8, pady=4
            )
            widget.configure(**btn_kwargs)
            bind_hover_classic_button(widget, palette)
        except Exception:
            pass

    if cls in ("Entry", "Text"):
        try:
            widget.configure(bg=palette["bg"], fg=palette["text"], insertbackground=palette["text"], bd=0)
        except Exception:
            pass

    if cls == "Checkbutton":
        try:
            cbtn_kwargs = dict(
                bg=palette["bg"],
                fg=palette["text"],
                activebackground=palette["button_bg"],
                activeforeground=palette["button_active_bg"],
                selectcolor=palette["button_bg"],
                bd=0,
                relief="flat",
                highlightthickness=0,
                padx=8,
                pady=4,
                disabledforeground=palette.get("palette", "button_disabled_color")
            )
            widget.configure(**cbtn_kwargs)
        except Exception:
            pass

    # ttk-specific instances
    try:
        if isinstance(widget, ttk.Progressbar):
            widget.configure(style="Aqua.Horizontal.TProgressbar")
    except Exception:
        pass

    try:
        if isinstance(widget, ttk.Button):
            widget.configure(style="Aqua.Dark.TButton")
    except Exception:
        pass

    try:
        if isinstance(widget, ttk.Label):
            widget.configure(style="Aqua.Dark.TLabel")
    except Exception:
        pass

    try:
        if isinstance(widget, ttk.Frame):
            widget.configure(style="Aqua.Dark.TFrame")
    except Exception:
        pass

    try:
        if isinstance(widget, ttk.Checkbutton):
            widget.configure(style="Aqua,Dark.TFrame")
    except Exception:
        pass

    for child in widget.winfo_children():
        set_color(child, palette)

def get_colors(path="resources/themes/default.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def hex_to_rgb(hex_color):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color!r}")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
