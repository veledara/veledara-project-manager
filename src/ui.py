import os
import tkinter as tk
from tkinter import ttk, messagebox
import json

import sv_ttk
from src.project_manager import ProjectManager


class ProjectLauncher:
    def __init__(self, master, manager: ProjectManager):
        self.master = master
        self.master.title("Project Launcher")
        self.master.resizable(False, False)  # Запрещаем изменение размера окна
        self.master.attributes("-fullscreen", False)  # Запрещаем фуллскрин

        self.manager = manager
        self.projects = self.manager.projects

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)

        self.search_entry = ttk.Entry(master, textvariable=self.search_var, width=50)
        self.search_entry.pack(padx=10, pady=10)

        self.listbox = tk.Listbox(master, width=80, height=20)
        self.listbox.pack(padx=10, pady=(0, 10))

        # Привязка событий
        self.search_entry.bind("<Down>", self.move_down_from_se)
        self.search_entry.bind("<Up>", self.move_up_from_se)
        self.search_entry.bind("<Return>", self.handle_return)

        self.listbox.bind("<Return>", self.open_project)
        self.listbox.bind("<Double-1>", self.open_project)
        self.listbox.bind("<Escape>", self.focus_search)
        self.listbox.bind("<KeyPress>", self.handle_keypress)

        self.listbox.bind("<Up>", self.move_selection_up)
        self.listbox.bind("<Down>", self.move_selection_down)

        self.search_entry.focus_set()
        self.update_list()

        # Кнопка для открытия окна настроек
        self.settings_button = ttk.Button(
            master, text="Настройки", command=self.open_settings_window
        )
        self.settings_button.pack(padx=10, pady=(5, 10))

        # Применение темы, если она сохранена
        self.apply_theme(self.manager.theme_dark)

    def open_settings_window(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Настройки")
        settings_window.geometry("400x250")
        settings_window.resizable(False, False)
        settings_window.attributes("-fullscreen", False)

        # Путь к VSCode
        self.vscode_path_var = tk.StringVar(value=self.manager.vscode_path or "")
        ttk.Label(settings_window, text="Путь к VSCode:").pack(padx=10, pady=5)
        self.vscode_entry = ttk.Entry(
            settings_window, textvariable=self.vscode_path_var, width=40
        )
        self.vscode_entry.pack(padx=10, pady=5)

        # Путь к главной директории
        self.main_dir_var = tk.StringVar(value=self.manager.projects_main_dir or "")
        ttk.Label(settings_window, text="Главная директория:").pack(padx=10, pady=5)
        self.main_dir_entry = ttk.Entry(
            settings_window, textvariable=self.main_dir_var, width=40
        )
        self.main_dir_entry.pack(padx=10, pady=5)

        # Тумблер для смены темы
        self.theme_var = tk.BooleanVar(
            value=self.manager.theme_dark
        )  # False для светлой, True для темной
        theme_switch = ttk.Checkbutton(
            settings_window, text="Темная тема", variable=self.theme_var
        )
        theme_switch.pack(padx=10, pady=5)

        self.apply_theme(self.theme_var.get())

        save_button = ttk.Button(
            settings_window, text="Сохранить", command=self.save_settings
        )
        save_button.pack(padx=10, pady=10)

    def save_settings(self):
        new_vscode_path = self.vscode_path_var.get()
        new_main_dir = self.main_dir_var.get()

        paths_changed = (new_vscode_path != self.manager.vscode_path) or (
            new_main_dir != self.manager.projects_main_dir
        )

        self.manager.set_vscode_path(new_vscode_path)
        self.manager.set_main_project_dir(new_main_dir)

        settings = {
            "vscode_path": new_vscode_path,
            "projects_main_dir": new_main_dir,
            "theme_dark": self.theme_var.get(),
        }

        with open("settings.json", "w") as f:
            json.dump(settings, f)

        self.apply_theme(self.theme_var.get())

        if paths_changed:
            self.manager.update_manager()

        self.update_list()

        # messagebox.showinfo("Настройки", "Настройки успешно сохранены.")

    def apply_theme(self, dark_mode: bool):
        """Применение темы: светлая или темная"""
        if dark_mode:
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")

    def move_down_from_se(self, event):
        self.handle_down(self)
        self.move_selection_down(self)

    def move_up_from_se(self, event):
        self.handle_up(self)
        self.move_selection_up(self)

    def move_selection_up(self, event):
        selection = self.listbox.curselection()
        if selection and selection[0] > 0:
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(selection[0] - 1)
            self.listbox.see(selection[0] - 1)
        return "break"

    def move_selection_down(self, event):
        selection = self.listbox.curselection()
        if selection and selection[0] < self.listbox.size() - 1:
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(selection[0] + 1)
            self.listbox.see(selection[0] + 1)
        return "break"

    def handle_down(self, event):
        if self.listbox.size() > 0:
            if not self.listbox.curselection():
                self.listbox.select_set(0)
            self.listbox.focus_set()
        return "break"

    def handle_up(self, event):
        if self.listbox.size() > 0:
            if not self.listbox.curselection():
                self.listbox.select_set(tk.END)
            self.listbox.focus_set()
        return "break"

    def handle_return(self, event):
        if self.listbox.size() == 1:
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(0)
            self.open_project(event)
        elif self.listbox.size() > 0:
            if not self.listbox.curselection():
                self.listbox.select_set(0)
            self.listbox.focus_set()
        return "break"

    def handle_keypress(self, event):
        if event.keysym in ("BackSpace", "Delete"):
            self.search_entry.focus_set()
            if self.search_var.get():
                if event.keysym == "BackSpace":
                    self.search_var.set(self.search_var.get()[:-1])
            return "break"

        if len(event.char) == 1 and event.char.isprintable():
            self.search_entry.focus_set()
            self.search_var.set(self.search_var.get() + event.char)
            self.search_entry.icursor(tk.END)
        return "break"

    def focus_search(self, event):
        self.search_entry.focus_set()
        return "break"

    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)

        for project in self.projects:
            project_path = project["path"]
            rel_path = os.path.relpath(
                project_path, self.manager.projects_main_dir
            ).lower()

            if search_term in rel_path:
                display_name = rel_path
                self.listbox.insert(tk.END, display_name)

        if self.listbox.size() > 0:
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(0)

    def open_project(self, event):
        selection = self.listbox.curselection()
        if selection:
            selected_project = self.listbox.get(selection[0])
            project_path = os.path.join(
                self.manager.projects_main_dir, selected_project
            )
            self.manager.open_in_vscode(project_path)
