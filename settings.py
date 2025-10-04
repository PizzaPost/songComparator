import json
import os
import tkinter.messagebox

import customtkinter

import misc


def submit_settings(lang, theme, appearance_mode, language):
    with open("resources/settings.json", "w") as f:
        json.dump({"theme": theme, "appearance_mode": appearance_mode, "language": language}, f)
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

    submit = customtkinter.CTkButton(frame, text="Submit" if not lang else lang["settings"]["submit"],
                                     command=lambda: submit_settings(lang, themes_dropdown.get(), dark_mode.get(),
                                                                     language_dropdown.get()))

    frame.pack(fill="both", expand=True, padx=5, pady=5)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    title.grid(row=0, column=0, columnspan=2, pady=5, sticky="n")
    seperator1.grid(row=1, column=0)
    themes_heading.grid(row=2, column=0, padx=5, sticky="w")
    themes_dropdown.grid(row=3, column=0, padx=5, sticky="w")
    warning1.grid(row=3, column=1, padx=5, sticky="e")
    dark_mode.grid(row=4, column=0, padx=5, pady=15, sticky="w")
    warning2.grid(row=4, column=1, padx=5, sticky="e")
    seperator2.grid(row=5, column=0)
    language_heading.grid(row=6, column=0, padx=5, sticky="w")
    language_dropdown.grid(row=7, column=0, padx=5, pady=5, sticky="w")
    seperator3.grid(row=8)
    submit.grid(row=9, column=0, columnspan=2, pady=5, sticky="n")
    tk.mainloop()


if __name__ == "__main__":
    open_settings()
