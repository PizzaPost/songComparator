# checks default installed modules
try:
    import tkinter.ttk
    import tkinter.messagebox
    import os
    import urllib.request
    import threading
    import json
except ImportError as e:
    print(f"Error: '{e.name}' not found. Please install it using 'pip install {e.name}'.")
    exit()

finished_steps = 0
done_event = threading.Event()
necessary_files = ["resources/assets/icon.png"]
custom_modules = ["data", "main", "stats", "visuals", "window"]
trying = True
palette = None


def installer():
    """installs the programm"""
    global finished_steps, trying
    try:
        while trying:
            try:
                # checks other modules
                import pyvidplayer2
                finished_steps = 2
                import pygame
                finished_steps = 3

                # checks custom modules
                import data
                finished_steps = 4
                import main
                finished_steps = 5
                import stats
                finished_steps = 6
                import visuals
                finished_steps = 7
                import window
                finished_steps = 8

                trying = False
            except ImportError as e:
                if not e.name in custom_modules:
                    os.system(f"pip install {e.name}")
                else:
                    link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/{e.name}.py"
                    urllib.request.urlretrieve(link, f"{e.name}.py")

        # create the necessary folders
        os.makedirs("resources/covers", exist_ok=True)
        finished_steps += 1
        os.makedirs("resources/details", exist_ok=True)
        finished_steps += 1
        os.makedirs("resources/playlists", exist_ok=True)
        finished_steps += 1
        os.makedirs("resources/tracks", exist_ok=True)
        finished_steps += 1
        os.makedirs("resources/data", exist_ok=True)
        finished_steps += 1
        os.makedirs("resources/themes", exist_ok=True)
        finished_steps += 1
        os.makedirs("resources/assets", exist_ok=True)
        finished_steps += 1

        for file in necessary_files:
            finished_steps += 1
            if not os.path.exists(file):
                link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/{file}"
                urllib.request.urlretrieve(link, file)
    except Exception as e:
        tkinter.messagebox.showerror("Installation Error", str(e))
    finally:
        done_event.set()


def load_palette(filename="resources/themes/default.json"):
    """Loads the palette from a JSON file."""
    global palette
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


palette = load_palette()


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


def set_color(widget):
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
        set_color(child)

def start_gui():
    """Starts the installer GUI."""
    global finished_steps
    #downloads the icon
    file="resources/assets/icon.ico"
    if not os.path.exists(file):
        try:
            os.makedirs("resources/assets", exist_ok=True)
            link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/{file}"
            urllib.request.urlretrieve(link, file)
            finished_steps += 1
        except Exception as e:
            tkinter.messagebox.showerror("Installation Error", f"Failed to Download the Icon for the installer {str(e)}")
            exit(0)
    tk = tkinter.Tk()
    tk.title("Installer")
    tk.iconbitmap(file)
    tk.geometry(f"400x185+{tk.winfo_screenwidth() // 2 - 208}+{tk.winfo_screenheight() // 2 - 88}")
    tk.resizable(False, False)
    tk.overrideredirect = True
    tk.configure(bg=palette["bg"])
    installation_text1 = tkinter.Label(tk, text="Installing...")
    installation_text2 = tkinter.Label(tk, text=f"Finished Steps: {finished_steps}/16")
    loading_bar = tkinter.ttk.Progressbar(tk, maximum=14, length=360)
    installation_text3 = tkinter.Label(tk, text="Please wait until installation is complete.")
    installation_text1.pack(padx=20, pady=20)
    installation_text2.pack(padx=20)
    loading_bar.pack(padx=20, pady=20)
    installation_text3.pack(padx=20)
    for widget in tk.winfo_children():
        set_color(widget)

    def run_now():
        """Runs the main program."""
        try:
            import main
            main.run()
        except Exception as e:
            tkinter.messagebox.showerror("Run error", f"Could not start program:\n{e}")
        tk.destroy()

    def update_ui():
        """Updates the installer GUI."""
        installation_text2.config(text=f"Finished Steps: {finished_steps}/16")
        loading_bar["value"] = finished_steps
        if done_event.is_set():
            tk.title("Installation Complete")
            for widget in tk.winfo_children():
                widget.destroy()
            frame = tkinter.Frame(tk)
            open_text1 = tkinter.Label(frame, text="Do you want to run the program?")
            yes_button = tkinter.Button(frame, text="Yes", command=lambda: run_now())
            no_button = tkinter.Button(frame, text="No", command=tk.destroy)
            for widget in tk.winfo_children():
                set_color(widget)
            frame.pack(padx=20, pady=20)
            open_text1.grid(row=0, column=0, columnspan=2, pady=30)
            yes_button.grid(row=1, column=0)
            no_button.grid(row=1, column=1)
        else:
            tk.after(1, update_ui)

    threading.Thread(target=installer, daemon=True).start()
    tk.after(1, update_ui)
    tk.mainloop()


if __name__ == "__main__":
    start_gui()
