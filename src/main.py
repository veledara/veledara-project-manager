import tkinter as tk

from src.project_manager import ProjectManager
from src.ui import ProjectLauncher


def main():
    projects_dir = r"D:\dev"
    vscode_path = r"D:\Program Files\Microsoft VS Code\Code.exe"

    manager = ProjectManager()

    manager.set_main_project_dir(projects_dir)
    manager.set_vscode_path(vscode_path)

    root = tk.Tk()
    app = ProjectLauncher(root, manager)
    root.mainloop()


if __name__ == "__main__":
    main()
