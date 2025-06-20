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
        self.crop_box_rect = None
        self.zoom_level = 1.0
        self.canvas_img_id = None

        self.zoom_level = 1.0
        self.canvas_img_id = None
        self.pan_x = 0
        self.pan_y = 0
        self.drag_start = None
        self.space_pressed = False
        self.left_dragging = False

        self.coord_label = None
        self.original_filename = ""
        self.zoom_cache = {}

        self.setup_widgets()

    def setup_widgets(self):
        # ─── LEFT PANEL ──────────────────────────────────
        left = tk.Frame(self.root)
        left.pack(side="left", padx=10, pady=10)

        tk.Button(left, text="Choose Image File", command=self.select_image_file).pack(pady=(0,5))
        self.image_label = tk.Label(left, text="No image selected", wraplength=300)
        self.image_label.pack()

        self.canvas = tk.Canvas(left, width=400, height=400, bg="gray")
        self.canvas.pack(pady=(10, 0))
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.do_pan)
        self.canvas.focus_set()

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



        self.slider = tk.Scale(right, from_=8, to=96, resolution=8, orient="horizontal")
        self.slider.set(20)
        self.slider.pack(pady=(0, 0))
        tk.Label(right, text="Crop Box Size").pack(pady=(0,10))

        tk.Label(right, text="Box Coordinates:").pack(pady=(8, 0))
        self.coord_label = tk.Label(right, text="(x, y)", font=("Courier", 10))
        self.coord_label.pack(pady=(0, 20))

        tk.Label(right, text="Save As Filename:").pack()
        self.filename_entry = tk.Entry(right)
        self.filename_entry.insert(0, "filename")
        self.filename_entry.pack()

        tk.Button(right, text="Choose Save Directory", command=self.select_dir).pack(pady=(10,0))
        self.dir_label = tk.Label(right, text="No directory selected", wraplength=200)
        self.dir_label.pack()

        tk.Button(right, text="Save Cropped Image", command=self.save_cropped).pack(pady=10)

        self.canvas.bind("<ButtonPress-1>", self.on_left_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<KeyPress-space>", self.on_space_down)
        self.canvas.bind("<KeyRelease-space>", self.on_space_up)

    def on_zoom(self, event):
        if event.delta > 0 or event.num == 4:
            self.zoom_level *= 1.1
        elif event.delta < 0 or event.num == 5:
            self.zoom_level /= 1.1

        min_zoom_x = 400 / self.img.width
        min_zoom_y = 400 / self.img.height
        min_zoom = max(min_zoom_x, min_zoom_y)
        self.zoom_level = max(min_zoom, min(self.zoom_level, 5.0))
        self.display_image()

    def select_image_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not path:
            return
        self.image_path = path
        self.image_label.config(text=path)
        self.img = load_image(path)
        self.zoom_cache.clear()
        self.original_filename = os.path.basename(path)
        self.display_image()

    def display_image(self):
        if self.img is None:
            return

        zoom = self.zoom_level
        box_size = 400
        img_w, img_h = self.img.size

        zoomed_w = int(img_w * zoom)
        zoomed_h = int(img_h * zoom)
        if zoom not in self.zoom_cache:
            zoomed = self.img.resize((zoomed_w, zoomed_h), Image.Resampling.LANCZOS)
            self.zoom_cache[zoom] = zoomed
        else:
            zoomed = self.zoom_cache[zoom]

        max_x = max(0, zoomed_w - box_size)
        max_y = max(0, zoomed_h - box_size)
        self.pan_x = max(0, min(self.pan_x, max_x))
        self.pan_y = max(0, min(self.pan_y, max_y))

        cropped = zoomed.crop((
            self.pan_x,
            self.pan_y,
            self.pan_x + box_size,
            self.pan_y + box_size
        ))

        self.tk_img = ImageTk.PhotoImage(cropped)

        self.canvas.delete("all")
        self.canvas_img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def preview_at_coords(self, canvas_x, canvas_y):
        if self.img is None:
            return

        box_size = self.slider.get()
        zoom = self.zoom_level

        img_x = int((self.pan_x + canvas_x) / zoom)
        img_y = int((self.pan_y + canvas_y) / zoom)

        self.coord_label.config(text=f"({img_x}, {img_y})")

        # Update default filename
        basename = os.path.splitext(self.original_filename)[0]
        auto_name = f"{basename}_{img_x}_{img_y}"
        self.filename_entry.delete(0, tk.END)
        self.filename_entry.insert(0, auto_name)

        self.cropped_img = crop_image(self.img, img_x, img_y, box_size)
        if not self.cropped_img:
            return

        preview_pixel = self.cropped_img.resize((100, 100), Image.Resampling.NEAREST)
        preview_smooth = self.cropped_img.resize((100, 100), Image.Resampling.LANCZOS)

        self.preview_tk_pixel = ImageTk.PhotoImage(preview_pixel)
        self.preview_tk_smooth = ImageTk.PhotoImage(preview_smooth)

        self.preview_canvas_pixel.delete("all")
        self.preview_canvas_pixel.create_image(0, 0, anchor="nw", image=self.preview_tk_pixel)
        self.preview_canvas_smooth.delete("all")
        self.preview_canvas_smooth.create_image(0, 0, anchor="nw", image=self.preview_tk_smooth)

        canvas_box_size = box_size * self.zoom_level
        half = canvas_box_size / 2
        x0, y0 = canvas_x - half, canvas_y - half
        x1, y1 = canvas_x + half, canvas_y + half

        if self.crop_box_rect:
            self.canvas.delete(self.crop_box_rect)

        self.crop_box_rect = self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=1)

    def on_canvas_click(self, event):
        self.preview_at_coords(event.x, event.y)

    def start_pan(self, event):
        self.drag_start = (event.x, event.y)

    def do_pan(self, event):
        if self.drag_start is None:
            return

        dx = event.x - self.drag_start[0]
        dy = event.y - self.drag_start[1]

        self.pan_x -= dx
        self.pan_y -= dy
        self.drag_start = (event.x, event.y)

        self.display_image()

    def on_space_down(self, event):
        self.space_pressed = True

    def on_space_up(self, event):
        self.space_pressed = False

    def on_left_click(self, event):
        self.left_dragging = True
        if self.space_pressed:
            self.start_pan(event)
        else:
            self.start_live_preview(event)

    def on_left_release(self, event):
        self.left_dragging = False
        if self.space_pressed:
            self.drag_start = None  # stop pan
        else:
            self.stop_live_preview(event)

    def select_dir(self):
        dir_ = filedialog.askdirectory()
        if not dir_:
            return
        self.dir_label.config(text=dir_)

    def start_live_preview(self, event):
        self.live_preview = True
        self.preview_at_coords(event.x, event.y)

    def stop_live_preview(self, event):
        self.live_preview = False

    def on_mouse_move(self, event):
        if self.space_pressed and self.left_dragging:
            self.do_pan(event)
        elif self.live_preview:
            self.preview_at_coords(event.x, event.y)

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