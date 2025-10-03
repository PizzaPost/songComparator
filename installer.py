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

try:
    import colors
except ImportError:
    link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/colors.py"
    urllib.request.urlretrieve(link, f"colors.py")

finished_steps = 1
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
                finished_steps = 3
                import pygame
                finished_steps = 4
                import customtkinter
                finished_steps = 5

                # checks custom modules
                import data
                finished_steps = 6
                import main
                finished_steps = 7
                import stats
                finished_steps = 8
                import visuals
                finished_steps = 9
                import window
                finished_steps = 10

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

palette = colors.load_palette()

def start_gui():
    """Starts the installer GUI."""
    global finished_steps
    # downloads the icon
    file = "resources/assets/icon.ico"
    if not os.path.exists(file):
        try:
            os.makedirs("resources/assets", exist_ok=True)
            link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/{file}"
            urllib.request.urlretrieve(link, file)
            finished_steps += 1
        except Exception as e:
            tkinter.messagebox.showerror("Installation Error",
                                         f"Failed to Download the Icon for the installer {str(e)}")
            exit(0)
    tk = tkinter.Tk()
    tk.title("Installer")
    tk.iconbitmap(file)
    tk.geometry(f"400x185+{tk.winfo_screenwidth() // 2 - 208}+{tk.winfo_screenheight() // 2 - 88}")
    tk.resizable(False, False)
    tk.overrideredirect = True
    tk.configure(bg=palette["bg"])
    installation_text1 = tkinter.Label(tk, text="Installing...")
    installation_text2 = tkinter.Label(tk, text=f"Finished Steps: {finished_steps}/18")
    loading_bar = tkinter.ttk.Progressbar(tk, maximum=14, length=360)
    installation_text3 = tkinter.Label(tk, text="Please wait until installation is complete.")
    installation_text1.pack(padx=20, pady=20)
    installation_text2.pack(padx=20)
    loading_bar.pack(padx=20, pady=20)
    installation_text3.pack(padx=20)
    for widget in tk.winfo_children():
        colors.set_color(widget, palette)

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
        installation_text2.config(text=f"Finished Steps: {finished_steps}/18")
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
                colors.set_color(widget, palette)
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
