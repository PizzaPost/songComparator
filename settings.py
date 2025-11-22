import json
import os
import tkinter.messagebox

import PIL as pillow
import customtkinter
import matplotlib.font_manager
from customtkinter import CTkImage

import main
import misc


def submit_settings(tk, lang, theme, appearance_mode, language, font_dropdown, font_specifier, font_list, master_volume,
                    track_volume, gui_volume,
                    effects_volume,
                    enabled_audio, logging):
    main.save_log("submitting settings")
    selected_font_name = font_dropdown.get()
    font = os.path.join("resurces", "fonts", "NotoSans.ttf")
    if selected_font_name == "NotoSans (default)":
        font = os.path.join("resurces", "fonts", "NotoSans.ttf")
    else:
        matching_fonts = [f for f in font_list if
                          matplotlib.font_manager.FontProperties(fname=f).get_name() == selected_font_name]
        if matching_fonts:
            font = matching_fonts[0]
            if font_specifier.get() != "Select a specific version.":
                font = font_specifier.get()
    misc.unhide_file(os.path.join("resources", "settings.json"))
    with open(os.path.join("resources", "settings.json"), "w") as f:
        json.dump({"theme": theme, "appearance_mode": appearance_mode, "language": language, "font": font,
                   "master_volume": int(master_volume), "track_volume": int(track_volume),
                   "gui_volume": int(gui_volume), "effects_volume": int(effects_volume),
                   "enabled_audio": enabled_audio,
                   "logging": True if logging == ("Enabled" if not lang else lang["settings"]["enabled"]) else False},
                  f, indent=4)
    f.close()
    misc.hide_file(os.path.join("resources", "settings.json"))
    tkinter.messagebox.showinfo(
        "Info",
        "Changed will be displayed after a restarting." if not lang else lang["settings"]["submit_info"])
    close_settings(tk, True)
    main.save_log("finished submitting settings")


def update_font_specifier(lang, font_specifier, selected, font_list, startup=False, font_path=None):
    matching_fonts = [f for f in font_list if matplotlib.font_manager.FontProperties(fname=f).get_name() == selected]
    if selected == "NotoSans (default)" or len(matching_fonts) < 2:
        font_specifier.grid_forget()
    else:
        font_specifier.grid(row=8, column=1, columnspan=2, padx=5, pady=5, sticky="w")
    font_specifier.configure(values=matching_fonts)
    if startup:
        font_specifier.set(font_path)
    else:
        font_specifier.set("Select a specific version." if not lang else lang["settings"]["font_specifier_info"])


def open_settings():
    main.save_log("starting settings")
    lang = misc.load_language(misc.load_settings())
    with open(os.path.join("resources", "settings.json"), "r") as f:
        data = json.load(f)
    f.close()
    themes = [theme.replace(".json", "") for theme in os.listdir("resources/themes")]
    languages = [language.replace(".json", "") for language in os.listdir("resources/languages")]
    customtkinter.set_appearance_mode(data["appearance_mode"])
    customtkinter.set_default_color_theme(f"resources/themes/{data['theme']}.json")
    theme_colors = json.load(open(f"resources/themes/{data["theme"]}.json", "r"))
    tk = customtkinter.CTk()
    tk.overrideredirect(True)
    tk.title("Settings" if not lang else lang["settings"]["title"])
    tk.geometry(f"650x370+{tk.winfo_screenwidth() // 2 - 325}+{tk.winfo_screenheight() // 2 - 185}")
    tk.resizable(False, False)
    tk.attributes("-topmost", True)
    tk.attributes("-alpha", 0)

    logging_var = tkinter.StringVar(value="Enabled" if data["logging"] else "Disabled")

    frame = customtkinter.CTkScrollableFrame(tk)
    frame2 = customtkinter.CTkFrame(frame)
    frame3 = customtkinter.CTkFrame(frame)

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
    title = customtkinter.CTkLabel(frame2, text="Settings" if not lang else lang["settings"]["title"],
                                   font=(font, 32, "bold"))
    seperator1 = customtkinter.CTkLabel(frame2, text="")
    themes_heading = customtkinter.CTkLabel(frame2, text="Themes" if not lang else lang["settings"]["themes"],
                                            font=(font, 24, "bold"))
    themes_dropdown = customtkinter.CTkOptionMenu(frame2, values=themes)
    warning1 = customtkinter.CTkLabel(frame2,
                                      text="⚠️ Please install more themes to use this feature ⚠️" if not lang else
                                      lang["settings"]["warning1"], text_color="red")
    if len(themes) <= 1:
        themes_dropdown.configure(state="disabled")
    dark_mode = customtkinter.CTkOptionMenu(frame2, values=["Dark", "Light"])
    dark_mode.set(data["appearance_mode"])
    warning2 = customtkinter.CTkLabel(frame2,
                                      text="⚠️ This feature may not be available for every theme ⚠️" if not lang else
                                      lang["settings"]["warning2"], text_color="orange")
    seperator2 = customtkinter.CTkLabel(frame2, text="")
    language_heading = customtkinter.CTkLabel(frame2, text="Text" if not lang else lang["settings"]["text"],
                                              font=(font, 24, "bold"))
    language_dropdown = customtkinter.CTkOptionMenu(frame2, values=languages)
    language_dropdown.set(data["language"])
    font_list = matplotlib.font_manager.findSystemFonts()
    font_list.sort(key=lambda font_name: matplotlib.font_manager.FontProperties(fname=font_name).get_name())
    font_list.insert(0, "resources/fonts/NotoSans.ttf")
    names = ["NotoSans (default)" if font_name == "resources/fonts/NotoSans.ttf"
             else matplotlib.font_manager.FontProperties(fname=font_name).get_name()
             for font_name in font_list]
    names = list(dict.fromkeys(names))
    font_dropdown = customtkinter.CTkOptionMenu(frame2, values=names,
                                                command=lambda selected: update_font_specifier(lang, font_specifier,
                                                                                               font_dropdown.get(),
                                                                                               font_list))
    font_dropdown.set(matplotlib.font_manager.FontProperties(fname=data["font"]).get_name())
    font_specifier = customtkinter.CTkOptionMenu(frame2, values=None)
    font_specifier.set(data["font"])
    update_font_specifier(lang, font_specifier, font_dropdown.get(), font_list, True, data["font"])
    seperator3 = customtkinter.CTkLabel(frame2, text="")
    audio_heading = customtkinter.CTkLabel(frame2, text="Audio" if not lang else lang["settings"]["audio"],
                                           font=(font, 24, "bold"))
    master_volume_label = customtkinter.CTkLabel(frame2, text=f"Master Volume:" if not lang else lang["settings"][
        "master_volume_label"])
    mute_img = CTkImage(light_image=pillow.Image.open("resources/assets/mute.png"),
                        dark_image=pillow.Image.open("resources/assets/mute.png"), size=(25, 25))
    master_volume_mute = customtkinter.CTkButton(frame2, text="", image=mute_img, width=1, height=1,
                                                 fg_color="transparent", hover_color=frame2.cget("fg_color"),
                                                 command=lambda: change_everything(
                                                     [master_volume, track_volume, gui_volume, effects_volume],
                                                     theme_colors))
    master_volume = customtkinter.CTkSlider(frame2, from_=0, to=100,
                                            state="normal" if data["enabled_audio"][0] else "disabled",
                                            command=lambda event: update_volume(master_volume_percentage,
                                                                                master_volume.get()))
    master_volume.set(data["master_volume"])
    value = int(master_volume.get())
    master_volume_percentage = customtkinter.CTkLabel(frame2,
                                                      text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")
    seperator4 = customtkinter.CTkLabel(frame2, text="━" * 200, height=20, text_color="gray30")
    track_volume_label = customtkinter.CTkLabel(frame2, text=f"Track Volume:" if not lang else lang["settings"][
        "track_volume_label"])
    track_volume_mute = customtkinter.CTkButton(frame2, text="", image=mute_img, width=1, height=1,
                                                fg_color="transparent", hover_color=frame2.cget("fg_color"),
                                                command=lambda: change_state(track_volume, theme_colors))
    track_volume = customtkinter.CTkSlider(frame2, from_=0, to=100,
                                           state="normal" if data["enabled_audio"][1] else "disabled",
                                           command=lambda event: update_volume(track_volume_percentage,
                                                                               track_volume.get()))
    track_volume.set(data["track_volume"])
    value = int(track_volume.get())
    track_volume_percentage = customtkinter.CTkLabel(frame2,
                                                     text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")
    gui_volume_label = customtkinter.CTkLabel(frame2,
                                              text=f"GUI Volume:" if not lang else lang["settings"]["gui_volume_label"])
    gui_volume_mute = customtkinter.CTkButton(frame2, text="", image=mute_img, width=1, height=1,
                                              fg_color="transparent",
                                              hover_color=frame2.cget("fg_color"),
                                              command=lambda: change_state(gui_volume, theme_colors))
    gui_volume = customtkinter.CTkSlider(frame2, from_=0, to=100,
                                         state="normal" if data["enabled_audio"][2] else "disabled",
                                         command=lambda event: update_volume(gui_volume_percentage, gui_volume.get()))
    gui_volume.set(data["gui_volume"])
    value = int(gui_volume.get())
    gui_volume_percentage = customtkinter.CTkLabel(frame2,
                                                   text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")
    effects_volume_label = customtkinter.CTkLabel(frame2, text=f"Effects Volume:" if not lang else lang["settings"][
        "effects_volume_label"])
    effects_volume_mute = customtkinter.CTkButton(frame2, text="", image=mute_img, width=1, height=1,
                                                  fg_color="transparent", hover_color=frame2.cget("fg_color"),
                                                  command=lambda: change_state(effects_volume, theme_colors))
    effects_volume = customtkinter.CTkSlider(frame2, from_=0, to=100,
                                             state="normal" if data["enabled_audio"][3] is True else "disabled",
                                             command=lambda event: update_volume(effects_volume_percentage,
                                                                                 effects_volume.get()))
    effects_volume.set(data["effects_volume"])
    value = int(effects_volume.get())
    effects_volume_percentage = customtkinter.CTkLabel(frame2,
                                                       text=f"{"   " if value < 100 else ""}{"  " if value < 10 else ""}{value}%")
    seperator5 = customtkinter.CTkLabel(frame2, text="")
    advanced_heading = customtkinter.CTkLabel(frame2, text="Advanced" if not lang else lang["settings"]["advanced"],
                                              font=(font, 24, "bold"))
    logging_label = customtkinter.CTkLabel(frame2, text="Logger")
    logging_button = customtkinter.CTkSegmentedButton(frame2,
                                                      values=["Enabled" if not lang else lang["settings"]["enabled"],
                                                              "Disabled" if not lang else lang["settings"]["disabled"]],
                                                      variable=logging_var)
    seperator6 = customtkinter.CTkLabel(frame2, text="")
    submit = customtkinter.CTkButton(frame3, text="Submit" if not lang else lang["settings"]["submit"],
                                     command=lambda: submit_settings(tk, lang, themes_dropdown.get(), dark_mode.get(),
                                                                     language_dropdown.get(), font_dropdown,
                                                                     font_specifier, font_list,
                                                                     master_volume.get(), track_volume.get(),
                                                                     gui_volume.get(), effects_volume.get(),
                                                                     [False if master_volume.cget(
                                                                         "state") == "disabled" else True,
                                                                      False if track_volume.cget(
                                                                          "state") == "disabled" else True,
                                                                      False if gui_volume.cget(
                                                                          "state") == "disabled" else True,
                                                                      False if effects_volume.cget(
                                                                          "state") == "disabled" else True],
                                                                     logging_button.get()))
    close = customtkinter.CTkButton(frame3, text="Close" if not lang else lang["settings"]["close"],
                                    command=lambda: close_settings(tk, False))

    frame.pack(fill="both", expand=True, padx=5, pady=5)
    frame2.pack()
    frame2.grid_columnconfigure(0, weight=1)
    frame2.grid_columnconfigure(1, weight=1)
    frame3.pack()

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
    font_dropdown.grid(row=8, column=0, padx=5, pady=5, sticky="w")
    seperator3.grid(row=9)
    audio_heading.grid(row=10, column=0, pady=5, sticky="w")
    master_volume_label.grid(row=11, column=0, padx=5, sticky="w")
    master_volume_mute.grid(row=11, column=1, padx=5, sticky="e")
    master_volume.grid(row=11, column=2, padx=5, sticky="e")
    master_volume_percentage.grid(row=11, column=3, padx=5, sticky="e")
    seperator4.grid(row=12, column=0, columnspan=4)
    track_volume_label.grid(row=13, column=0, padx=5, sticky="w")
    track_volume_mute.grid(row=13, column=1, padx=5, sticky="e")
    track_volume.grid(row=13, column=2, padx=5, sticky="e")
    track_volume_percentage.grid(row=13, column=3, padx=5, sticky="e")
    gui_volume_label.grid(row=14, column=0, padx=5, sticky="w")
    gui_volume_mute.grid(row=14, column=1, padx=5, sticky="e")
    gui_volume.grid(row=14, column=2, padx=5, sticky="e")
    gui_volume_percentage.grid(row=14, column=3, padx=5, sticky="e")
    effects_volume_label.grid(row=15, column=0, padx=5, sticky="w")
    effects_volume_mute.grid(row=15, column=1, padx=5, sticky="e")
    effects_volume.grid(row=15, column=2, padx=5, sticky="e")
    effects_volume_percentage.grid(row=15, column=3, padx=5, sticky="e")
    seperator5.grid(row=16)
    advanced_heading.grid(row=17, column=0, pady=5, sticky="w")
    logging_label.grid(row=18, column=0, padx=5, sticky="w")
    logging_button.grid(row=18, column=0, padx=5, sticky="e")
    seperator6.grid(row=19)
    submit.grid(row=20, column=0, columnspan=2, padx=15, pady=5, sticky="n")
    close.grid(row=20, column=2, columnspan=2, padx=15, pady=5, sticky="n")
    update_slider_colors([master_volume, track_volume, gui_volume, effects_volume], theme_colors)
    tk.update()
    tk.withdraw()
    main.save_log("opened settings successfully")
    return tk, frame


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


def close_settings(tk, saved):
    if saved or tkinter.messagebox.askyesno("Close",
                                            "Are you sure you want to close the settings without saving?"):
        tk.withdraw()
        main.save_log("closed settings without saving" if not saved else "closed settings with saving")


if __name__ == "__main__":
    pass
