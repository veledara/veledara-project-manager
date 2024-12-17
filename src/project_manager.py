import os
import subprocess
import json


class ProjectManager:
    def __init__(self) -> None:
        self.projects_main_dir: str = None
        self.vscode_path: str = None
        self.theme_dark: bool = False
        self.update_manager()

    def update_manager(self):
        self.load_settings()
        self.projects = self.scan_projects()


    def load_settings(self):
        # Загружаем настройки из файла, если он существует
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    content = f.read().strip()  # Читаем содержимое и убираем лишние пробелы
                    if content:  # Если файл не пустой
                        settings = json.loads(content)
                        self.vscode_path = settings.get("vscode_path", None)
                        self.projects_main_dir = settings.get("projects_main_dir", None)
                        self.theme_dark = settings.get("theme_dark", False)
                    else:
                        # Если файл пустой, устанавливаем значения по умолчанию
                        self.vscode_path = None
                        self.projects_main_dir = None
                        self.theme_dark = False
            except json.JSONDecodeError:
                # Если ошибка при чтении JSON (например, поврежденный файл), устанавливаем значения по умолчанию
                self.vscode_path = None
                self.projects_main_dir = None
                self.theme_dark = False
        else:
            # Если файл не существует, устанавливаем значения по умолчанию
            self.vscode_path = None
            self.projects_main_dir = None
            self.theme_dark = False

    def set_main_project_dir(self, projects_main_dir):
        if not os.path.exists(projects_main_dir):
            print(f"Директория {projects_main_dir} не существует.")
            return

        self.projects_main_dir = projects_main_dir

    def set_vscode_path(self, vscode_path):
        if not os.path.exists(vscode_path):
            print(f"Директория {vscode_path} не существует.")
            return

        self.vscode_path = vscode_path

    def scan_projects(self):
        projects = []
        if self.projects_main_dir is None:
            print("Нужно выбрать главную папку.")
            return projects

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
            "Python": {"requirements.txt", "pyproject.toml"},
            "JavaScript": {"package.json"},
            "Java": {"pom.xml", "build.gradle"},
            "Rust": {"Cargo.toml"},
            "Go": {"go.mod"},
        }

        for root, dirs, files in os.walk(self.projects_main_dir, topdown=True):
            is_project = False
            project_type = []

            if ".git" in dirs or ".git" in files:
                is_project = True
                project_type.append("Git")

            for lang, indicators in project_indicators.items():
                if any(indicator in files for indicator in indicators):
                    is_project = True
                    project_type.append(lang)

            if is_project:
                project_info = {"path": root, "types": project_type}
                projects.append(project_info)

            dirs[:] = [d for d in dirs if d not in ignored_folders]

        return projects

    def open_in_vscode(self, project_path):
        try:
            subprocess.Popen([self.vscode_path, project_path])
        except FileNotFoundError:
            print("Не удалось найти VS Code.")
        except Exception as e:
            print(f"Ошибка при открытии проекта: {e}")
