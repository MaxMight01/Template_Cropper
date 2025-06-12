# gui.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from logic import load_image, crop_image, save_image

class ImageCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Template Cropper")
        self.root.resizable(False, False)
        self.root.geometry("700x500")

        self.image_path = None
        self.img = None
        self.tk_img = None
        self.cropped_img = None
        self.live_preview = False

        self.setup_widgets()

    def setup_widgets(self):
        # ─── LEFT PANEL ──────────────────────────────────
        left = tk.Frame(self.root)
        left.pack(side="left", padx=10, pady=10)

        tk.Button(left, text="Choose Image File", command=self.select_image_file).pack(pady=(0,5))
        self.image_label = tk.Label(left, text="No image selected", wraplength=300)
        self.image_label.pack()

        self.canvas = tk.Canvas(left, width=400, height=400, bg="gray")
        self.canvas.pack(pady=(10, 0), fill="none", expand=False)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # ─── RIGHT PANEL ─────────────────────────────────
        right_wrapper = tk.Frame(self.root)
        right_wrapper.pack(side="right", fill="both", expand=True)

        top_spacer = tk.Frame(right_wrapper)
        top_spacer.pack(fill="both", expand=True)
        right = tk.Frame(right_wrapper)
        right.pack()
        bottom_spacer = tk.Frame(right_wrapper)
        bottom_spacer.pack(fill="both", expand=True)

        tk.Label(right, text="Preview: Raw (Left) vs AA (Right)").pack()


        preview_frame = tk.Frame(right)
        preview_frame.pack(pady=(0, 10))

        self.preview_canvas_pixel = tk.Canvas(preview_frame, width=100, height=100, bg="white")
        self.preview_canvas_pixel.pack(side="left", padx=5)

        self.preview_canvas_smooth = tk.Canvas(preview_frame, width=100, height=100, bg="white")
        self.preview_canvas_smooth.pack(side="left", padx=5)


        self.slider = tk.Scale(right, from_=2, to=50, resolution=2, orient="horizontal", label="Crop Box Size")
        self.slider.set(20)
        self.slider.pack(pady=(10, 10))

        tk.Label(right, text="Save As Filename:").pack()
        self.filename_entry = tk.Entry(right)
        self.filename_entry.pack()

        tk.Button(right, text="Choose Save Directory", command=self.select_dir).pack(pady=(10,0))
        self.dir_label = tk.Label(right, text="No directory selected", wraplength=200)
        self.dir_label.pack()

        tk.Button(right, text="Save Cropped Image", command=self.save_cropped).pack(pady=10)

    def select_image_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not path:
            return
        self.image_path = path
        self.image_label.config(text=path)
        self.img = load_image(path)
        self.display_image()

    def display_image(self):
        resized = self.img.resize((400, 400), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def on_canvas_click(self, event):
        if self.img is None:
            return

        box_size = self.slider.get()
        x_ratio = self.img.width / 400
        y_ratio = self.img.height / 400
        click_x = int(event.x * x_ratio)
        click_y = int(event.y * y_ratio)

        self.cropped_img = crop_image(self.img, click_x, click_y, box_size)
        if not self.cropped_img:
            messagebox.showerror("Error", "Crop area out of bounds!")
            return

        preview_pixel = self.cropped_img.resize((100, 100), Image.Resampling.NEAREST)
        preview_smooth = self.cropped_img.resize((100, 100), Image.Resampling.LANCZOS)

        self.preview_tk_pixel = ImageTk.PhotoImage(preview_pixel)
        self.preview_tk_smooth = ImageTk.PhotoImage(preview_smooth)

        self.preview_canvas_pixel.delete("all")
        self.preview_canvas_pixel.create_image(0, 0, anchor="nw", image=self.preview_tk_pixel)

        self.preview_canvas_smooth.delete("all")
        self.preview_canvas_smooth.create_image(0, 0, anchor="nw", image=self.preview_tk_smooth)

    def select_dir(self):
        dir_ = filedialog.askdirectory()
        if not dir_:
            return
        self.dir_label.config(text=dir_)

    def save_cropped(self):
        if self.cropped_img is None:
            messagebox.showerror("Error", "No crop selected!")
            return

        filename = self.filename_entry.get().strip()
        dir_ = self.dir_label.cget("text")
        if not filename or dir_ == "No directory selected":
            messagebox.showerror("Error", "Missing filename or directory.")
            return

        full_path = os.path.join(dir_, filename + ".png")
        try:
            save_image(self.cropped_img, full_path)
            messagebox.showinfo("Saved", f"Image saved to:\n{full_path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))