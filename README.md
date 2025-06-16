# Template Cropper

![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Preview and crop image patches of fixed size by clicking or dragging on an image. Live preview shows raw and antialised versions side-by-side. Includes zoom, pan, and pixel-precise control over box size. The interface is built via `tkinter` and `Pillow`.

## Using the application
Navigate to the `dist` directory and run the executable:
```sh
.\dist\TemplateCropper.exe
```
The app opens a GUI window with two panels. The usage is as follows:
1. **Choose image file**: Select the image you want to crop from. The parent image is displayed on a fixed 400x400 canvas.
2. **Zoom and Pan**: Scroll to zoom in/out. Right-click + drag to pan across. Alternatively, hold Spacebar + Left-click + drag to pan across.
3. **Box Size**: Use the slider to set the crop box size.
4. **Crop**: Hold left-click on the parent image to preview the crop in real-time. Let go to lock in the preview. A thin rectangle shows where the preview is being taken from.
5. **Preview**: A raw-pixels preview and an antialiased preview are displayed.
6. **Save Cropped Image**: Enter the filename (extension not needed) and choose a save directory. Click *Save Cropped Image*. A `.png` is saved. The default name follows `x_y_filename.png` where `(x, y)` are the box coordinates.

### Optional: Building from Source (if needed)
Requires Python + pip + `pyinstaller`. To build a fresh `.exe`:
```sh
pip install -r requirements.txt
pyinstaller --onefile --windowed --name TemplateCropper --icon=T.ico --add-data "T.ico;." template_cropper.py
```
This will create a self-contained `TemplateCropper.exe` in the `dist` directory.

---
Thanks for using! Feel free to fork, improve, or report bugs.