from gui import ImageCropperApp
import tkinter as tk
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Template Cropper")

    icon_path = resource_path("T.ico")
    root.iconbitmap(icon_path)

    app = ImageCropperApp(root)
    root.mainloop()