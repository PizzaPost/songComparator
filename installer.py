import os
import platform
import tkinter.messagebox

# os check
current_os = platform.system()
supported_os = ["Windows", "Linux", "Darwin"]
if current_os not in supported_os:
    tkinter.messagebox.showerror("Unsupported OS",
                                 f"Oh looks like you're using {current_os}. This program is only supported on Windows, Linux and macOS.")
    exit()

import json

try:
    import misc

    lang = misc.load_language(misc.load_settings())
    color_path = os.path.join("resources", "themes", f"{misc.load_settings()["theme"]}.json")
except ImportError:
    lang = None
    color_path = os.path.join("resources", "themes", "default.json")
finished_steps = 1
import tkinter.ttk
import urllib.request
import threading
import shutil
import sys

if current_os == "Windows":
    import ctypes


def hide_file(file):
    """Hides a file or directory using OS-specific methods."""
    if current_os == "Windows":
        ctypes.windll.kernel32.SetFileAttributesW(file, 0x02)
    elif current_os == "Darwin":
        os.system(f'chflags hidden "{file}"')


try:
    import colors
except ImportError:
    link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/colors.py"
    urllib.request.urlretrieve(link, f"colors.py")
    hide_file("colors.py")
    import colors
finished_steps += 1
number_of_steps = 40
done_event = threading.Event()
final_done_event = threading.Event()
necessary_files = ["resources/assets/icon.png", "resources/assets/icon_white.png", "resources/assets/mute.png",
                   "resources/assets/star.png", "resources/assets/star_filled.png", "resources/assets/icon_glow.png",
                   "resources/assets/star_highlighted.png",
                   "resources/assets/tnf.png",
                   "resources/languages/Deutsch.json", "resources/languages/English.json",
                   "resources/fonts/NotoEmoji.ttf", "resources/fonts/NotoSans.ttf", "resources/fonts/NotoSansBold.ttf"]
custom_modules = ["colors", "data", "main", "misc", "settings", "stats", "visuals"]
official_modules = ["pyvidplayer2", "pygame", "customtkinter", "yt-dlp", "pillow", "matplotlib"]
trying = True
palette = colors.load_palette(color_path)
failed_to_install_pywin_things = False
failed_to_install_winshell = False
event_trigger = 0
create_desktop_shortcut = None


def installer():
    """installs the program"""
    global finished_steps, trying, failed_to_install_pywin_things, failed_to_install_winshell
    settings_path = os.path.join("resources", "settings.json")
    if not os.path.exists(settings_path):
        with open(settings_path, "w") as f:
            json.dump({"theme": "default", "appearance_mode": "Dark", "language": "English",
                       "font": os.path.join("resources", "fonts", "NotoSans.ttf"), "master_volume": 100,
                       "track_volume": 100, "gui_volume": 100, "effects_volume": 100,
                       "enabled_audio": [True, True, True, True], "logging": False, "performance": False,
                       "fps": 120}, f, indent=4)
        f.close()
        hide_file(settings_path)
    finished_steps += 1
    while trying:
        try:
            # checks other modules
            import pyvidplayer2
            finished_steps = 6
            import pygame
            finished_steps = 7
            import customtkinter
            finished_steps = 8
            import yt_dlp
            finished_steps = 9
            import PIL
            finished_steps = 10
            import matplotlib
            finished_steps = 11
            if current_os == "Windows":
                if not failed_to_install_pywin_things:
                    from win32com.client import Dispatch
                if not failed_to_install_winshell:
                    import winshell
            finished_steps = 13

            # checks custom modules
            import data
            finished_steps = 14
            import main
            finished_steps = 15
            import misc
            finished_steps = 16
            import settings
            finished_steps = 17
            import stats
            finished_steps = 18
            import visuals
            finished_steps = 19

            trying = False
        except ImportError as e:
            if not e.name in custom_modules:
                if e.name == "yt_dlp":
                    os.system(f"pip install yt-dlp")
                elif e.name == "PIL":
                    os.system(f"pip install pillow")
                elif e.name in ("win32com", "pywintypes"):
                    if not failed_to_install_pywin_things:
                        os.system(f"pip install pywin32")
                        failed_to_install_pywin_things = True
                elif e.name == "winshell":
                    if not failed_to_install_winshell:
                        os.system(f"pip install winshell")
                        failed_to_install_winshell = True
                else:
                    os.system(f"pip install {e.name}")
            else:
                link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/{e.name}.py"
                urllib.request.urlretrieve(link, f"{e.name}.py")
                hide_file(f"{e.name}.py")
    try:
        # create the necessary folders
        os.makedirs(os.path.join("resources", "covers"), exist_ok=True)
        finished_steps += 1
        os.makedirs(os.path.join("resources", "details"), exist_ok=True)
        finished_steps += 1
        os.makedirs(os.path.join("resources", "playlists"), exist_ok=True)
        finished_steps += 1
        os.makedirs(os.path.join("resources", "tracks"), exist_ok=True)
        finished_steps += 1
        os.makedirs(os.path.join("resources", "data"), exist_ok=True)
        hide_file(os.path.join("resources", "data"))
        finished_steps += 1
        os.makedirs(os.path.join("resources", "themes"), exist_ok=True)
        hide_file(os.path.join("resources", "themes"))
        finished_steps += 1
        os.makedirs(os.path.join("resources", "assets"), exist_ok=True)
        hide_file(os.path.join("resources", "assets"))
        finished_steps += 1
        os.makedirs(os.path.join("resources", "languages"), exist_ok=True)
        hide_file(os.path.join("resources", "languages"))
        finished_steps += 1
        os.makedirs(os.path.join("resources", "fonts"), exist_ok=True)
        hide_file(os.path.join("resources", "fonts"))
        finished_steps += 1


        for file in necessary_files:
            finished_steps += 1
            local_path = os.path.normpath(file)
            if not os.path.exists(local_path):
                link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/{file}"
                urllib.request.urlretrieve(link, local_path)
    except Exception as e:
        tkinter.messagebox.showerror("Installation Error" if not lang else lang["error"]["installation_error_title"],
                                     str(e))
    finally:
        done_event.set()


finished_steps += 1


def create_shortcut(desktop_shortcut_value, desktop):
    if desktop_shortcut_value:
        path_to_here = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(path_to_here, "main.py")
        if desktop:
            if current_os == "Windows":
                import winshell
                target_folder = winshell.desktop()
            else:
                target_folder = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            target_folder = path_to_here
        if current_os == "Windows":
            import winshell
            from win32com.client import Dispatch
            shortcut_path = os.path.join(target_folder, "Song Comparator.lnk")
            python_dir = os.path.dirname(sys.executable)
            pythonw = os.path.join(python_dir, "pythonw.exe")
            if not os.path.exists(pythonw):
                pythonw = sys.executable
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = pythonw
            shortcut.Arguments = f'"{script_path}" --quiet'
            shortcut.WorkingDirectory = path_to_here
            shortcut.IconLocation = os.path.join(path_to_here, "resources", "assets", "icon.ico")
            shortcut.Description = "Launch Song Comparator"
            shortcut.Save()
        elif current_os == "Linux":
            shortcut_path = os.path.join(target_folder, "SongComparator.desktop")
            icon_path = os.path.join(path_to_here, "resources", "assets", "icon.png")
            desktop_entry = f"""[Desktop Entry]
                                Type=Application
                                Name=Song Comparator
                                Comment=Launch Song Comparator
                                Exec={sys.executable} "{script_path}"
                                Path={path_to_here}
                                Icon={icon_path}
                                Terminal=false
                                Categories=Audio;Video;
                            """
            with open(shortcut_path, "w") as f:
                f.write(desktop_entry)
            os.chmod(shortcut_path, 0o755)
        elif current_os == "Darwin":
            shortcut_path = os.path.join(target_folder, "Song Comparator.command")
            command_content = f"""#!/bin/bash
                                cd "{path_to_here}"
                                "{sys.executable}" "{script_path}"
                                """
            with open(shortcut_path, "w") as f:
                f.write(command_content)
            os.chmod(shortcut_path, 0o755)
    final_done_event.set()


def uninstaller(tk):
    """Shows the uninstaller UI."""
    tk.columnconfigure(0, weight=0)
    tk.columnconfigure(1, weight=0)
    tk.rowconfigure(0, weight=0)
    tk.rowconfigure(1, weight=0)
    for widget in tk.winfo_children():
        widget.destroy()
    tk.title("Uninstaller" if not lang else lang["uninstaller"]["title"])
    frame = tkinter.Frame(tk)
    frame.pack(fill="both", expand=True)
    frame.delete_assets = tkinter.BooleanVar(value=True)
    frame.delete_code = tkinter.BooleanVar(value=True)
    frame.delete_track_related_stuff = tkinter.BooleanVar()
    frame.delete_themes = tkinter.BooleanVar(value=True)
    frame.delete_settings = tkinter.BooleanVar()
    frame.delete_modules = tkinter.BooleanVar()
    delete_assets_checkbox = tkinter.Checkbutton(frame, text="Delete Assets" if not lang else lang["uninstaller"][
        "delete_assets"], variable=frame.delete_assets)
    delete_code_checkbox = tkinter.Checkbutton(frame, text="Delete Code" if not lang else lang["uninstaller"][
        "delete_code"], variable=frame.delete_code)
    delete_track_related_stuff_checkbox = tkinter.Checkbutton(frame, text="Delete Tracks" if not lang else
    lang["uninstaller"]["delete_tracks"], variable=frame.delete_track_related_stuff)
    delete_themes_checkbox = tkinter.Checkbutton(frame, text="Delete Themes" if not lang else lang["uninstaller"][
        "delete_themes"], variable=frame.delete_themes)
    delete_settings_checkbox = tkinter.Checkbutton(frame, text="Delete Settings" if not lang else lang["uninstaller"][
        "delete_settings"], variable=frame.delete_settings)
    delete_modules_checkbox = tkinter.Checkbutton(frame, text="Delete Modules" if not lang else lang["uninstaller"][
        "delete_modules"], variable=frame.delete_modules)
    start_uninstall = tkinter.Button(frame, text="Uninstall" if not lang else lang["uninstaller"]["uninstall"],
                                     width=10, height=3,
                                     command=lambda: threading.Thread(target=uninstall,
                                                                      args=(frame.delete_assets.get(),
                                                                            frame.delete_code.get(),
                                                                            frame.delete_track_related_stuff.get(),
                                                                            frame.delete_themes.get(),
                                                                            frame.delete_settings.get(),
                                                                            frame.delete_modules.get()),
                                                                      daemon=True).start())
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)
    delete_assets_checkbox.grid(row=0, column=0, sticky="w", padx=5, pady=3)
    delete_code_checkbox.grid(row=1, column=0, sticky="w", padx=5, pady=3)
    delete_track_related_stuff_checkbox.grid(row=2, column=0, sticky="w", padx=5, pady=3)
    delete_themes_checkbox.grid(row=3, column=0, sticky="w", padx=5, pady=3)
    delete_settings_checkbox.grid(row=4, column=0, sticky="w", padx=5, pady=3)
    delete_modules_checkbox.grid(row=5, column=0, sticky="w", padx=5, pady=3)
    start_uninstall.grid(row=0, column=1, rowspan=5, sticky="e", padx=14)
    for widget in tk.winfo_children():
        colors.set_color(widget, palette)

    def uninstall(assets, code, tracks, themes, settings, modules):
        """Uninstalls the wanted files."""
        for widget in tk.winfo_children():
            widget.destroy()
        tk.title("Uninstalling..." if not lang else lang["uninstaller"]["uninstalling"])
        uninstalling_text1 = tkinter.Label(tk,
                                           text="Uninstalling..." if not lang else lang["uninstaller"]["uninstalling"])
        uninstalling_text2 = tkinter.Label(tk,
                                           text=f"This should not take long." if not lang else lang["uninstaller"][
                                               "waiting"])
        loading_bar = tkinter.ttk.Progressbar(tk, maximum=10, length=360, mode="indeterminate")
        loading_bar.start()
        uninstalling_text1.pack(padx=20, pady=20)
        uninstalling_text2.pack(padx=20)
        loading_bar.pack(padx=20, pady=20)
        for widget in tk.winfo_children():
            colors.set_color(widget, palette)
        tk.protocol("WM_DELETE_WINDOW", lambda: None)
        trying = True
        all = False
        if assets and tracks and themes and settings:
            all = True
        while trying:
            try:
                if assets:
                    assets = False
                    shutil.rmtree(os.path.join("resources", "assets"))
                    shutil.rmtree(os.path.join("resources", "languages"))
                if code:
                    code = False
                    os.remove("colors.py")
                    os.remove("data.py")
                    os.remove("main.py")
                    os.remove("misc.py")
                    os.remove("settings.py")
                    os.remove("stats.py")
                    os.remove("visuals.py")
                    if current_os == "Windows":
                        os.remove("Song Comparator.lnk")
                    elif current_os == "Linux":
                        os.remove("SongComparator.desktop")
                    elif current_os == "Darwin":
                        os.remove("Song Comparator.command")
                    shortcut_path = ""
                    if current_os == "Windows":
                        import winshell
                        target_folder = winshell.desktop()
                        shortcut_path = os.path.join(target_folder, "Song Comparator.lnk")
                    elif current_os == "Linux":
                        target_folder = os.path.join(os.path.expanduser("~"), "Desktop")
                        shortcut_path = os.path.join(target_folder, "SongComparator.desktop")
                    elif current_os == "Darwin":
                        target_folder = os.path.join(os.path.expanduser("~"), "Desktop")
                        shortcut_path = os.path.join(target_folder, "Song Comparator.command")
                    if os.path.exists(shortcut_path):
                        os.remove(shortcut_path)
                if tracks:
                    tracks = False
                    shutil.rmtree(os.path.join("resources", "covers"))
                    shutil.rmtree(os.path.join("resources", "data"))
                    shutil.rmtree(os.path.join("resources", "details"))
                    shutil.rmtree(os.path.join("resources", "playlists"))
                    shutil.rmtree(os.path.join("resources", "tracks"))
                if themes:
                    themes = False
                    shutil.rmtree(os.path.join("resources", "themes"))
                if settings:
                    settings = False
                    os.remove(os.path.join("resources", "settings.json"))
                if modules:
                    modules = False
                    for module in official_modules:
                        os.system(f"pip uninstall --yes {module}")
                if all:
                    all = False
                    shutil.rmtree("resources")
                trying = False
            except FileNotFoundError:
                pass
        for widget in tk.winfo_children():
            widget.destroy()
        # Shows the finished installation view
        tk.protocol("WM_DELETE_WINDOW", lambda: tk.destroy())
        tk.title("Uninstalled" if not lang else lang["uninstaller"]["uninstalled"])
        uninstalling_text1 = tkinter.Label(tk, text="Uninstalled" if not lang else lang["uninstaller"]["uninstalled"])
        uninstalling_text2 = tkinter.Label(tk, text="You can close this app now." if not lang else lang["uninstaller"][
            "you_can_close"])
        uninstalling_text1.pack(padx=20, pady=20)
        uninstalling_text2.pack(padx=20)
        for widget in tk.winfo_children():
            colors.set_color(widget, palette)


def start_installation(tk):
    """Shows the installation view."""
    for widget in tk.winfo_children():
        widget.destroy()
    tk.protocol("WM_DELETE_WINDOW", lambda: None)
    installation_text1 = tkinter.Label(tk, text="Installing..." if not lang else lang["installer"]["installing"])
    installation_text2 = tkinter.Label(tk,
                                       text=f"Finished Steps: {finished_steps}/{number_of_steps}" if not lang else
                                       lang["installer"][
                                           "finished_steps"].format(finished_steps, number_of_steps))
    loading_bar = tkinter.ttk.Progressbar(tk, maximum=number_of_steps, length=360)
    installation_text3 = tkinter.Label(tk, text="Please wait until installation is complete." if not lang else
    lang["installer"]["please_wait"])
    installation_text1.pack(padx=20, pady=20)
    installation_text2.pack(padx=20)
    loading_bar.pack(padx=20, pady=20)
    installation_text3.pack(padx=20)
    for widget in tk.winfo_children():
        colors.set_color(widget, palette)

    def run_now():
        """Runs the main program."""
        tk.destroy()
        try:
            import main
            main.run()
        except Exception as e:
            tkinter.messagebox.showerror("Run error" if not lang else lang["error"]["run_error_title"],
                                         f"Could not start program:\n{e}" if not lang else lang["error"][
                                             "run_error_description1"].format(str(e)))

    def update_ui():
        """Updates the installer GUI."""
        global event_trigger
        if not done_event.is_set():
            installation_text2.config(
                text=f"Finished Steps: {finished_steps}/{number_of_steps}" if not lang else lang["installer"][
                    "finished_steps"].format(
                    finished_steps, number_of_steps))
            loading_bar["value"] = finished_steps
        if done_event.is_set() and event_trigger == 0:
            event_trigger = 1
            for widget in tk.winfo_children():
                widget.destroy()
            frame = tkinter.Frame(tk)
            desktop_shortcut_checkbox = tkinter.Checkbutton(frame, text="Create desktop shortcut" if not lang else
            lang["installer"]["create_shortcut"], variable=create_desktop_shortcut)
            finalize_installation_button = tkinter.Button(frame,
                                                          text="Finish" if not lang else lang["installer"]["finish"],
                                                          command=lambda: create_shortcut(
                                                              create_desktop_shortcut.get(), True))
            for widget in tk.winfo_children():
                colors.set_color(widget, palette)
            frame.pack(padx=20, pady=20)
            desktop_shortcut_checkbox.grid(row=0, column=0, padx=20, pady=20)
            finalize_installation_button.grid(row=1, column=0)
        if final_done_event.is_set() and event_trigger == 1:
            create_shortcut(True, False)
            event_trigger = 2
            tk.protocol("WM_DELETE_WINDOW", lambda: tk.destroy())
            tk.title("Installation Complete" if not lang else lang["installer"]["installation_complete"])
            for widget in tk.winfo_children():
                widget.destroy()
            frame = tkinter.Frame(tk)
            open_text1 = tkinter.Label(frame, text="Do you want to run the program?" if not lang else lang["installer"][
                "run_now"])
            yes_button = tkinter.Button(frame, text="Yes" if not lang else lang["misc"]["yes"],
                                        command=lambda: run_now())
            no_button = tkinter.Button(frame, text="No" if not lang else lang["misc"]["no"], command=tk.destroy)
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


def start_gui():
    """Starts the installer GUI."""
    global finished_steps, create_desktop_shortcut
    icon_rel_path = "resources/assets/icon.ico"
    icon_path = os.path.normpath(icon_rel_path)
    if not os.path.exists(icon_path):
        try:
            os.makedirs(os.path.dirname(icon_path), exist_ok=True)
            link = f"https://raw.githubusercontent.com/PizzaPost/songComparator/master/{icon_rel_path}"
            urllib.request.urlretrieve(link, icon_path)
        except Exception as e:
            tkinter.messagebox.showerror(
                "Installation Error" if not lang else lang["error"]["installation_error_title"],
                f"Failed to Download the Icon for the installer:\n{str(e)}" if not lang else lang["error"][
                    "installation_error_description1"].format(str(e)))
            exit(0)
    finished_steps += 1
    tk = tkinter.Tk()
    create_desktop_shortcut = tkinter.BooleanVar(value=False)
    tk.title("Installer" if not lang else lang["installer"]["title"])
    tk.iconbitmap(icon_path)
    tk.geometry(f"400x185+{tk.winfo_screenwidth() // 2 - 208}+{tk.winfo_screenheight() // 2 - 88}")
    tk.resizable(False, False)
    tk.attributes("-topmost", True)
    tk.configure(bg=palette["bg"])
    frame = tkinter.Frame(tk)
    frame.grid(row=0, column=0, sticky="nsew")
    install_button = tkinter.Button(frame, text="Install" if not lang else lang["installer"]["install"], width=10,
                                    height=3, command=lambda: start_installation(tk))
    uninstall_button = tkinter.Button(frame, text="Uninstall" if not lang else lang["uninstaller"]["uninstall"],
                                      width=10,
                                      height=3, command=lambda: uninstaller(tk))
    tk.columnconfigure(0, weight=1)
    tk.columnconfigure(1, weight=1)
    tk.rowconfigure(0, weight=1)
    tk.rowconfigure(1, weight=1)
    install_button.grid(row=0, column=0, padx=15)
    uninstall_button.grid(row=0, column=1, padx=15)
    frame.update_idletasks()
    frame.grid_propagate(False)
    frame.place(relx=0.5, rely=0.5, anchor="center")
    for widget in tk.winfo_children():
        colors.set_color(widget, palette)
    tk.mainloop()


if __name__ == "__main__":
    start_gui()
