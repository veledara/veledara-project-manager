import os
import subprocess


class ProjectManager:
    def __init__(self) -> None:
        self.projects_main_dir: str = None
        self.vscode_path: str = None
        self.projects = self.scan_projects()

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

        print(f"Начинаю сканирование директории: {self.projects_main_dir}")

        for root, dirs, files in os.walk(self.projects_main_dir, topdown=True):
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

    def open_in_vscode(self, project_path):
        try:
            subprocess.Popen([self.vscode_path, project_path])
        except FileNotFoundError:
            print("Не удалось найти VS Code. Убедитесь, что VS Code доступен в PATH.")
        except Exception as e:
            print(f"Произошла ошибка при открытии проекта: {e}")
