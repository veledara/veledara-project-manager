import tkinter as tk

from src.project_manager import ProjectManager
from src.ui import ProjectLauncher


def main():
    manager = ProjectManager()

    root = tk.Tk()
    app = ProjectLauncher(root, manager)
    root.mainloop()


if __name__ == "__main__":
    main()
