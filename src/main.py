import os
import tkinter as tk
from tkinter import ttk
import subprocess


class ProjectLauncher:
    def __init__(self, master, projects_dir):
        self.master = master
        self.master.title("Project Launcher")
        self.projects_dir = projects_dir
        self.projects = self.scan_projects()

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)

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
        print("down")
        if self.listbox.size() > 0:
            if not self.listbox.curselection():
                self.listbox.select_set(0)
            self.listbox.focus_set()
        return "break"

    def handle_up(self, event):
        print("up")
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
        print("keypress")
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

    def scan_projects(self):
        projects = []
        ignored_folders = {
            "venv",
            ".venv",
            "node_modules",
            ".git",
            "dist",
            "__pycache__",
            ".idea",
        }
        project_indicators = {
            "Python": {"requirements.txt", "setup.py", "Pipfile", "pyproject.toml"},
            "JavaScript": {"package.json"},
            "Java": {"pom.xml", "build.gradle"},
            "Rust": {"Cargo.toml"},
            "Go": {"go.mod"},
        }

        print(f"Начинаю сканирование директории: {self.projects_dir}")

        for root, dirs, files in os.walk(self.projects_dir, topdown=True):
            # Проверяем является ли директория проектом
            is_project = False
            project_type = []

            # Проверка на Git проект
            if ".git" in dirs or ".git" in files:
                is_project = True
                project_type.append("Git")

            # Проверка на другие типы проектов
            for lang, indicators in project_indicators.items():
                if any(indicator in files for indicator in indicators):
                    is_project = True
                    project_type.append(lang)

            if is_project:
                project_info = {"path": root, "types": project_type}
                projects.append(project_info)
                print(f"Найден проект: {root} (Типы: {', '.join(project_type)})")
                dirs.clear()  # Пропускаем поддиректории
                continue

            # Фильтруем игнорируемые папки
            dirs[:] = [d for d in dirs if d not in ignored_folders]

        print(f"Всего найдено проектов: {len(projects)}")
        return projects

    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)

        for project in self.projects:
            project_path = project["path"]
            rel_path = os.path.relpath(project_path, self.projects_dir).lower()

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
            project_path = os.path.join(self.projects_dir, selected_project)
            self.open_in_vscode(project_path)

    def open_in_vscode(self, project_path):
        try:
            vscode_path = r"D:\Program Files\Microsoft VS Code\Code.exe"  # Укажите правильный путь
            subprocess.Popen([vscode_path, project_path])
        except FileNotFoundError:
            print("Не удалось найти VS Code. Убедитесь, что VS Code доступен в PATH.")
        except Exception as e:
            print(f"Произошла ошибка при открытии проекта: {e}")


def main():
    projects_dir = r"D:\dev"  # Замените на путь с проектами

    if not os.path.exists(projects_dir):
        print(f"Директория {projects_dir} не существует.")
        return

    print(f"Директория с проектами: {projects_dir} существует.")

    root = tk.Tk()
    app = ProjectLauncher(root, projects_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
