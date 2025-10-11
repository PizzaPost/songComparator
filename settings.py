import json
import os
import tkinter.messagebox

import PIL as pillow
import customtkinter
from customtkinter import CTkImage

import misc


def submit_settings(lang, theme, appearance_mode, language, master_volume, track_volume, gui_volume, effects_volume,
                    enabled_audio):
    with open("resources/settings.json", "w") as f:
        json.dump({"theme": theme, "appearance_mode": appearance_mode, "language": language,
                   "master_volume": int(master_volume), "track_volume": int(track_volume),
                   "gui_volume": int(gui_volume), "effects_volume": int(effects_volume),
                   "enabled_audio": enabled_audio}, f, indent=4)
    f.close()
    tkinter.messagebox.showinfo("Info", "Changed will be displayed after restarting.")


def open_settings():
    lang = misc.load_language()
    with open("resources/settings.json", "r") as f:
        data = json.load(f)
    f.close()
    themes = [theme.replace(".json", "") for theme in os.listdir("resources/themes")]
    languages = [language.replace(".json", "") for language in os.listdir("resources/languages")]
    customtkinter.set_appearance_mode(data["appearance_mode"])
    customtkinter.set_default_color_theme(f"resources/themes/{data['theme']}.json")
    theme_colors = json.load(open(f"resources/themes/{data["theme"]}.json", "r"))
    tk = customtkinter.CTk()
    tk.title("Settings" if not lang else lang["settings"]["title"])
    tk.geometry(f"650x370+{tk.winfo_screenwidth() // 2 - 325}+{tk.winfo_screenheight() // 2 - 185}")
    tk.resizable(False, False)
    tk.attributes("-topmost", True)

    frame = customtkinter.CTkScrollableFrame(tk)

    with open(f"resources/themes/{data["theme"]}.json", "r") as f:
        data2 = json.load(f)
        if os.name == "nt":
            font = data2["CTkFont"]["Windows"]
        elif os.name == "posix":
            font = data2["CTkFont"]["Linux"]
        elif os.name == "darwin":
            font = data2["CTkFont"]["macOS"]
        else:
            font = data2["CTkFont"]["default"]
    title = customtkinter.CTkLabel(frame, text="Settings" if not lang else lang["settings"]["title"],
                                   font=(font, 32, "bold"))
    seperator1 = customtkinter.CTkLabel(frame, text="")
    themes_heading = customtkinter.CTkLabel(frame, text="Themes" if not lang else lang["settings"]["themes"],
                                            font=(font, 24, "bold"))
    themes_dropdown = customtkinter.CTkOptionMenu(frame, values=themes)
    warning1 = customtkinter.CTkLabel(frame,
                                      text="⚠️ Please install more themes to use this feature ⚠️" if not lang else
                                      lang["settings"]["warning1"], text_color="red")
    if len(themes) <= 1:
        themes_dropdown.configure(state="disabled")
    dark_mode = customtkinter.CTkOptionMenu(frame, values=["System", "Dark", "Light"])
    dark_mode.set(data["appearance_mode"])
    warning2 = customtkinter.CTkLabel(frame,
                                      text="⚠️ This feature may not be available for every theme ⚠️" if not lang else
                                      lang["settings"]["warning2"], text_color="orange")
    seperator2 = customtkinter.CTkLabel(frame, text="")
    language_heading = customtkinter.CTkLabel(frame, text="Language" if not lang else lang["settings"]["language"],
                                              font=(font, 24, "bold"))
    language_dropdown = customtkinter.CTkOptionMenu(frame, values=languages)
    language_dropdown.set(data["language"])
    seperator3 = customtkinter.CTkLabel(frame, text="")
    audio_heading = customtkinter.CTkLabel(frame, text="Audio" if not lang else lang["settings"]["audio"],
                                           font=(font, 24, "bold"))
    master_volume_label = customtkinter.CTkLabel(frame, text=f"Master Volume:" if not lang else lang["settings"][
        "master_volume_label"])
    mute_img = CTkImage(light_image=pillow.Image.open("resources/assets/mute.png"),
                        dark_image=pillow.Image.open("resources/assets/mute.png"), size=(25, 25))
    master_volume_mute = customtkinter.CTkButton(frame, text="", image=mute_img, width=1, height=1,
                                                 fg_color="transparent", hover_color=frame.cget("fg_color"),
                                                 command=lambda: change_everything(
                                                     [master_volume, track_volume, gui_volume, effects_volume],
                                                     theme_colors))
    master_volume = customtkinter.CTkSlider(frame, from_=0, to=100,
                                            state="normal" if data["enabled_audio"][0] else "disabled",
                                            command=lambda event: update_volume(master_volume_percentage,
                                                                                master_volume.get()))
    master_volume.set(data["master_volume"])
    value = int(master_volume.get())
    master_volume_percentage = customtkinter.CTkLabel(frame,
                                                      text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")
    seperator4 = customtkinter.CTkLabel(frame, text="━" * 200, height=20, text_color="gray30")
    track_volume_label = customtkinter.CTkLabel(frame, text=f"Track Volume:" if not lang else lang["settings"][
        "track_volume_label"])
    track_volume_mute = customtkinter.CTkButton(frame, text="", image=mute_img, width=1, height=1,
                                                fg_color="transparent", hover_color=frame.cget("fg_color"),
                                                command=lambda: change_state(track_volume, theme_colors))
    track_volume = customtkinter.CTkSlider(frame, from_=0, to=100,
                                           state="normal" if data["enabled_audio"][1] else "disabled",
                                           command=lambda event: update_volume(track_volume_percentage,
                                                                               track_volume.get()))
    track_volume.set(data["track_volume"])
    value = int(track_volume.get())
    track_volume_percentage = customtkinter.CTkLabel(frame,
                                                     text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")
    gui_volume_label = customtkinter.CTkLabel(frame,
                                              text=f"GUI Volume:" if not lang else lang["settings"]["gui_volume_label"])
    gui_volume_mute = customtkinter.CTkButton(frame, text="", image=mute_img, width=1, height=1, fg_color="transparent",
                                              hover_color=frame.cget("fg_color"),
                                              command=lambda: change_state(gui_volume, theme_colors))
    gui_volume = customtkinter.CTkSlider(frame, from_=0, to=100,
                                         state="normal" if data["enabled_audio"][2] else "disabled",
                                         command=lambda event: update_volume(gui_volume_percentage, gui_volume.get()))
    gui_volume.set(data["gui_volume"])
    value = int(gui_volume.get())
    gui_volume_percentage = customtkinter.CTkLabel(frame,
                                                   text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")
    effects_volume_label = customtkinter.CTkLabel(frame, text=f"Effects Volume:" if not lang else lang["settings"][
        "effects_volume_label"])
    effects_volume_mute = customtkinter.CTkButton(frame, text="", image=mute_img, width=1, height=1,
                                                  fg_color="transparent", hover_color=frame.cget("fg_color"),
                                                  command=lambda: change_state(effects_volume, theme_colors))
    effects_volume = customtkinter.CTkSlider(frame, from_=0, to=100,
                                             state="normal" if data["enabled_audio"][3] is True else "disabled",
                                             command=lambda event: update_volume(effects_volume_percentage,
                                                                                 effects_volume.get()))
    effects_volume.set(data["effects_volume"])
    value = int(effects_volume.get())
    effects_volume_percentage = customtkinter.CTkLabel(frame,
                                                       text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")
    seperator5 = customtkinter.CTkLabel(frame, text="")
    submit = customtkinter.CTkButton(frame, text="Submit" if not lang else lang["settings"]["submit"],
                                     command=lambda: submit_settings(lang, themes_dropdown.get(), dark_mode.get(),
                                                                     language_dropdown.get(), master_volume.get(),
                                                                     track_volume.get(), gui_volume.get(),
                                                                     effects_volume.get(), [False if master_volume.cget(
                                             "state") == "disabled" else True, False if track_volume.cget(
                                             "state") == "disabled" else True, False if gui_volume.cget(
                                             "state") == "disabled" else True, False if effects_volume.cget(
                                             "state") == "disabled" else True]))

    frame.pack(fill="both", expand=True, padx=5, pady=5)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    title.grid(row=0, column=0, columnspan=4, pady=5, sticky="n")
    seperator1.grid(row=1, column=0)
    themes_heading.grid(row=2, column=0, padx=5, sticky="w")
    themes_dropdown.grid(row=3, column=0, padx=5, sticky="w")
    warning1.grid(row=3, column=0, columnspan=4, padx=5, sticky="e")
    dark_mode.grid(row=4, column=0, padx=5, pady=15, sticky="w")
    warning2.grid(row=4, column=0, columnspan=4, padx=5, sticky="e")
    seperator2.grid(row=5, column=0)
    language_heading.grid(row=6, column=0, padx=5, sticky="w")
    language_dropdown.grid(row=7, column=0, padx=5, pady=5, sticky="w")
    seperator3.grid(row=8)
    audio_heading.grid(row=9, column=0, pady=5, sticky="w")
    master_volume_label.grid(row=10, column=0, padx=5, sticky="w")
    master_volume_mute.grid(row=10, column=1, padx=5, sticky="e")
    master_volume.grid(row=10, column=2, padx=5, sticky="e")
    master_volume_percentage.grid(row=10, column=3, padx=5, sticky="e")
    seperator4.grid(row=11, column=0, columnspan=4)
    track_volume_label.grid(row=12, column=0, padx=5, sticky="w")
    track_volume_mute.grid(row=12, column=1, padx=5, sticky="e")
    track_volume.grid(row=12, column=2, padx=5, sticky="e")
    track_volume_percentage.grid(row=12, column=3, padx=5, sticky="e")
    gui_volume_label.grid(row=13, column=0, padx=5, sticky="w")
    gui_volume_mute.grid(row=13, column=1, padx=5, sticky="e")
    gui_volume.grid(row=13, column=2, padx=5, sticky="e")
    gui_volume_percentage.grid(row=13, column=3, padx=5, sticky="e")
    effects_volume_label.grid(row=14, column=0, padx=5, sticky="w")
    effects_volume_mute.grid(row=14, column=1, padx=5, sticky="e")
    effects_volume.grid(row=14, column=2, padx=5, sticky="e")
    effects_volume_percentage.grid(row=14, column=3, padx=5, sticky="e")
    seperator5.grid(row=15)
    submit.grid(row=16, column=0, columnspan=4, pady=5, sticky="n")
    update_slider_colors([master_volume, track_volume, gui_volume, effects_volume], theme_colors)
    tk.mainloop()


def change_everything(audio_widgets, theme_colors):
    state = "normal" if audio_widgets[0]._state == "normal" else "disabled"
    for widget in audio_widgets:
        change_state(widget, theme_colors, state)


def change_state(widget, theme_colors, state=None):
    if state == None:
        state = widget._state
    if state == "normal":
        widget.configure(state="disabled")
        widget.configure(progress_color=theme_colors["CTkSlider"]["progress_color_disabled"],
                         button_color=theme_colors["CTkSlider"]["button_color_disabled"],
                         button_hover_color=theme_colors["CTkSlider"]["button_color_disabled"])
    else:
        widget.configure(state="normal")
        widget.configure(progress_color=theme_colors["CTkSlider"]["progress_color"],
                         button_color=theme_colors["CTkSlider"]["button_color"],
                         button_hover_color=theme_colors["CTkSlider"]["button_hover_color"])


def update_volume(percentage_widget, value):
    value = int(value)
    percentage_widget.configure(text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")


def update_slider_colors(widgets, theme_colors):
    for widget in widgets:
        if widget._state == "normal":
            widget.configure(progress_color=theme_colors["CTkSlider"]["progress_color"],
                             button_color=theme_colors["CTkSlider"]["button_color"],
                             button_hover_color=theme_colors["CTkSlider"]["button_hover_color"])
        else:
            widget.configure(progress_color=theme_colors["CTkSlider"]["progress_color_disabled"],
                             button_color=theme_colors["CTkSlider"]["button_color_disabled"],
                             button_hover_color=theme_colors["CTkSlider"]["button_color_disabled"])


if __name__ == "__main__":
    open_settings()
