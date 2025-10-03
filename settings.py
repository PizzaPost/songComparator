import json
import os
import tkinter.messagebox

import customtkinter


def open_settings():
    themes=[theme.replace(".json", "") for theme in os.listdir("resources/themes")]
    languages=[language.replace(".json", "") for language in os.listdir("resources/languages")]
    customtkinter.set_default_color_theme("resources/themes/default.json")
    customtkinter.set_appearance_mode("dark")
    tk = customtkinter.CTk()
    tk.title("Settings")
    tk.geometry(f"500x300+{tk.winfo_screenwidth() // 2 - 200}+{tk.winfo_screenheight() // 2 - 150}")
    tk.resizable(False, False)
    tk.attributes("-topmost", True)

    frame=customtkinter.CTkFrame(tk)

    with open("resources/themes/default.json", "r") as f:
        data = json.load(f)
        if os.name == "nt":
            font = data["CTkFont"]["Windows"]
        elif os.name == "posix":
            font = data["CTkFont"]["Linux"]
        elif os.name == "darwin":
            font = data["CTkFont"]["macOS"]
        else:
            font = data["CTkFont"]["default"]
    title=customtkinter.CTkLabel(frame, text="Settings", font=(font, 32, "bold"))
    seperator1=customtkinter.CTkLabel(frame, text="")
    themes_heading=customtkinter.CTkLabel(frame, text="Themes", font=(font, 24, "bold"))
    themes_dropdown=customtkinter.CTkOptionMenu(frame, values=themes)
    warning1=customtkinter.CTkLabel(frame, text="⚠️ Please install more themes to use this feature ⚠️", text_color="red")
    if len(themes)<=1:
        themes_dropdown.configure(state="disabled")
    dark_mode = customtkinter.CTkSwitch(frame, text="Dark Mode", onvalue="dark", offvalue="light")
    warning2=customtkinter.CTkLabel(frame, text="⚠️ This feature may not be available for every theme ⚠️", text_color="orange")
    if customtkinter.get_appearance_mode() == "Dark":
        dark_mode.select()
    def toggle_dark_mode():
        if dark_mode.get():
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")
    dark_mode.configure(command=toggle_dark_mode)
    seperator2=customtkinter.CTkLabel(frame, text="")
    language_heading=customtkinter.CTkLabel(frame, text="Language", font=(font, 24, "bold"))
    language_dropdown=customtkinter.CTkOptionMenu(frame, values=languages)
    language_dropdown.set("English")



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
    tk.mainloop()


if __name__ == "__main__":
    open_settings()
