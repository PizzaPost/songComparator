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

finished_steps = 1
done_event = threading.Event()
necessary_files = []
custom_modules = ["data", "main", "stats", "visuals", "window"]
trying = True
palette = None


def load_palette(filename="resources/themes/default.json"):
    """Loads the palette from a JSON file."""
    global palette
    if palette: return palette
    default = {
        "background": "#0b0d0f",
        "card": "#0f1113",
        "text": "#e6e6e6",
        "muted_text": "#b9bdc1",
        "dark_red": "#7C0008",
        "light_red": "#EA5660",
        "button_bg": "#1a1c1e",
        "button_fg": "#f3f4f5",
        "button_active_bg": "#281213",
        "button_active_fg": "#ffffff",
        "border": "#232629",
        "progress_trough": "#151718",
        "progress_bar": "#7C0008"
    }

    if os.path.exists(filename):
        try:
            # loads existing palette
            with open(filename, "r", encoding="utf-8") as f:
                palette = json.load(f)
            f.close()
        except Exception:
            # creates default palette file
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4)
            f.close()
            palette = default
    else:
        # creates default palette file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)
        f.close()
        palette = default
    return palette


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
        for file in necessary_files:
            if not os.path.exists(file):
                link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/{file}"
                urllib.request.urlretrieve(link, file)

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
    except Exception as e:
        tkinter.messagebox.showerror("Installation Error", str(e))
    finally:
        done_event.set()


palette = load_palette()


def set_color(widget):
    """Styles 'widget' and its children using a theme loaded from colors.json."""
    # configure ttk styles once
    style = tkinter.ttk.Style()
    try:
        # prefer 'clam' for better control over progressbar colors, fallback silently if unavailable
        style.theme_use('clam')
    except Exception:
        pass

    style.configure('Dark.TLabel', background=palette['card'], foreground=palette['text'])
    style.configure('Dark.TFrame', background=palette['card'])
    style.configure('Dark.TButton',
                    background=palette['button_bg'],
                    foreground=palette['button_fg'],
                    relief='flat')
    style.map('Dark.TButton',
              background=[('active', palette['button_active_bg']), ('pressed', palette['button_active_bg'])],
              foreground=[('active', palette['button_active_fg']), ('pressed', palette['button_active_fg'])])
    # Progressbar style
    style.configure('Custom.Horizontal.TProgressbar',
                    troughcolor=palette['progress_trough'],
                    background=palette['progress_bar'],
                    bordercolor=palette['border'])

    # Apply to tk / classic widgets
    cls = widget.__class__.__name__

    # Frame
    if cls in ('Frame', 'LabelFrame'):
        try:
            widget.configure(bg=palette['card'], bd=0, highlightthickness=0)
        except Exception:
            pass

    # Label
    if cls == 'Label':
        try:
            widget.configure(bg=palette['card'], fg=palette['text'])
        except Exception:
            pass

    # Button
    if cls == 'Button':
        try:
            widget.configure(
                bg=palette['button_bg'],
                fg=palette['button_fg'],
                activebackground=palette['button_active_bg'],
                activeforeground=palette['button_active_fg'],
                bd=0,
                relief='flat',
                highlightthickness=0,
                padx=8, pady=4
            )
        except Exception:
            pass

    # Entry
    if cls in ('Entry', 'Text'):
        try:
            widget.configure(bg=palette['card'], fg=palette['text'], insertbackground=palette['text'], bd=0)
        except Exception:
            pass

    # ttk widgets
    if isinstance(widget, tkinter.ttk.Progressbar):
        try:
            widget.configure(style='Custom.Horizontal.TProgressbar', maximum=widget.cget("maximum"))
        except Exception:
            pass

    if isinstance(widget, tkinter.ttk.Button):
        try:
            widget.configure(style='Dark.TButton')
        except Exception:
            pass

    if isinstance(widget, tkinter.ttk.Label):
        try:
            widget.configure(style='Dark.TLabel')
        except Exception:
            pass

    if isinstance(widget, tkinter.ttk.Frame):
        try:
            widget.configure(style='Dark.TFrame')
        except Exception:
            pass

    # style children
    for child in widget.winfo_children():
        set_color(child)


def start_gui():
    """Starts the installer GUI."""
    global finished_steps
    tk = tkinter.Tk()
    tk.title("Installer")
    tk.geometry(f"400x185+{tk.winfo_screenwidth() // 2 - 208}+{tk.winfo_screenheight() // 2 - 88}")
    tk.resizable(False, False)
    tk.overrideredirect = True
    tk.configure(bg=palette['card'])
    installation_text1 = tkinter.Label(tk, text="Installing...")
    installation_text2 = tkinter.Label(tk, text=f"Finished Steps: {finished_steps}/14")
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
        installation_text2.config(text=f"Finished Steps: {finished_steps}/14")
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
