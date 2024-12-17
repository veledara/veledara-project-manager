import os
import tkinter as tk
from tkinter import ttk

from src.project_manager import ProjectManager


class ProjectLauncher:
    def __init__(self, master, manager: ProjectManager):
        self.master = master
        self.master.title("Project Launcher")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)

        self.manager = manager
        self.projects = self.manager.scan_projects()

        self.search_entry = ttk.Entry(master, textvariable=self.search_var, width=50)
        self.search_entry.pack(padx=10, pady=10)

        self.listbox = tk.Listbox(master, width=80, height=20)
        self.listbox.pack(padx=10, pady=(0, 10))

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
