import os, json, tkinter
def load_palette(filename="resources/themes/default.json"):
    """Loads the palette from a JSON file."""
    default = {
        "background": "#0b0d0f",
        "bg": "#0f1113",
        "text": "#e6e6e6",
        "dark_red": "#7C0008",
        "light_red": "#EA5660",
        "button_bg": "#1a1c1e",
        "button_fg": "#f3f4f5",
        "button_active_bg": "#EA5660",
        "border": "#232629",
        "progress_trough": "#151718",
        "progress_bar": "#7C0008",
        "hover_red": "#a33c43",
    }

    if os.path.exists(filename):
        try:
            # loads existing palette
            with open(filename, "r", encoding="utf-8") as f:
                palette = json.load(f)
            f.close()
        except Exception:
            # creates default palette file
            os.makedirs("resources/themes", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4)
            f.close()
            palette = default
    else:
        # creates default palette file
        os.makedirs("resources/themes", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)
        f.close()
        palette = default
    return palette

def bind_hover_classic_button(btn, palette):
    """Adds a hover style for buttons"""
    if getattr(btn, "_hover_bound", False):
        return
    btn._hover_bound = True
    try:
        btn._orig_bg = btn.cget("bg")
        btn._orig_fg = btn.cget("fg")
    except Exception:
        btn._orig_bg, btn._orig_fg = palette["button_bg"], palette["button_fg"]

    def on_enter(e):
        try:
            btn.configure(bg=palette["hover_red"], fg="#ffffff")
        except Exception:
            pass

    def on_leave(e):
        try:
            btn.configure(bg=btn._orig_bg, fg=btn._orig_fg)
        except Exception:
            pass

    btn.bind("<Enter>", on_enter, add="+")
    btn.bind("<Leave>", on_leave, add="+")
    # ensure pressed color is used when the button is pressed
    try:
        btn.configure(activebackground=palette["button_active_bg"], activeforeground="#ffffff")
    except Exception:
        pass


def set_color(widget, palette):
    """Apply an "aqua" themed dark mode."""
    style = tkinter.ttk.Style()
    # try to get a clean theme suitable for customizing
    for theme_try in ("aqua", "arc", "breeze", "yaru", "default"):
        try:
            style.theme_use(theme_try)
            break
        except Exception:
            continue

    # TTK styles
    style.configure("Aqua.Dark.TFrame", background=palette["bg"])
    style.configure("Aqua.Dark.TLabel", background=palette["bg"], foreground=palette["text"])
    style.configure("Aqua.Dark.TButton",
                    background=palette["button_bg"],
                    foreground=palette["button_fg"],
                    relief="flat",
                    padding=(8,4))
    style.map("Aqua.Dark.TButton",
              background=[("active", palette["hover_red"]), ("pressed", palette["button_active_bg"])],
              foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
    style.configure("Aqua.Horizontal.TProgressbar",
                    troughcolor=palette["progress_trough"],
                    background=palette["progress_bar"],
                    bordercolor=palette["border"])

    # apply to classic widget types
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
            widget.configure(bg=palette["button_bg"],
                             fg=palette["button_fg"],
                             activebackground=palette["light_red"],
                             activeforeground="#ffffff",
                             bd=0, relief="flat", padx=8, pady=4)
            bind_hover_classic_button(widget, palette)
        except Exception:
            pass

    if cls in ("Entry", "Text"):
        try:
            widget.configure(bg=palette["bg"], fg=palette["text"], insertbackground=palette["text"], bd=0)
        except Exception:
            pass

    # ttk-specific instances
    try:
        if isinstance(widget, tkinter.ttk.Progressbar):
            widget.configure(style="Aqua.Horizontal.TProgressbar")
    except Exception:
        pass

    try:
        if isinstance(widget, tkinter.ttk.Button):
            widget.configure(style="Aqua.Dark.TButton")
    except Exception:
        pass

    try:
        if isinstance(widget, tkinter.ttk.Label):
            widget.configure(style="Aqua.Dark.TLabel")
    except Exception:
        pass

    try:
        if isinstance(widget, tkinter.ttk.Frame):
            widget.configure(style="Aqua.Dark.TFrame")
    except Exception:
        pass

    # style every child widget
    for child in widget.winfo_children():
        set_color(child, palette)