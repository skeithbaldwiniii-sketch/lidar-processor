import tkinter as tk

from app.gui import LiDARProcessorGUI


def main():
    root = tk.Tk()
    app = LiDARProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()