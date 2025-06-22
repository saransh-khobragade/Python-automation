import os
import sys
import subprocess

# 📦 Auto-install dependencies
try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, UnidentifiedImageError

try:
    import rawpy
    import imageio
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rawpy", "imageio"])
    import rawpy
    import imageio

# Supported formats
COMMON_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.gif', '.heic', '.avif')
RAW_FORMATS = ('.cr2', '.nef', '.arw', '.dng', '.orf', '.rw2', '.raf', '.sr2', '.pef', '.raw')
ALL_FORMATS = COMMON_FORMATS + RAW_FORMATS

# Resize target (A4 in pixels at 150 DPI)
A4_SIZE = (1240, 1754)

def convert_raw_to_image(path):
    try:
        with rawpy.imread(path) as raw:
            rgb = raw.postprocess()
            return Image.fromarray(rgb)
    except Exception as e:
        print(f"❌ RAW error: {path} — {e}")
        return None

def load_image(path, resize=False):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in RAW_FORMATS:
            img = convert_raw_to_image(path)
        else:
            img = Image.open(path)
        if img is None:
            return None
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if resize:
            img = img.resize(A4_SIZE, Image.LANCZOS)
        return img
    except Exception as e:
        print(f"❌ Failed to load {path}: {e}")
        return None

def collect_images(path, recursive=False, resize=False):
    images = []
    for root, _, files in os.walk(path):
        for f in sorted(files):
            if f.lower().endswith(ALL_FORMATS):
                img = load_image(os.path.join(root, f), resize=resize)
                if img:
                    images.append(img)
        if not recursive:
            break
    return images

def create_pdf(images, output_path="merged_output.pdf", dpi=150):
    if not images:
        print("❌ No images to convert.")
        return
    try:
        images[0].save(
            output_path,
            "PDF",
            resolution=dpi,
            save_all=True,
            append_images=images[1:]
        )
        print(f"\n✅ PDF created: {output_path}")
    except Exception as e:
        print(f"❌ Error saving PDF: {e}")

# MAIN
if __name__ == "__main__":
    path = input("📂 Enter image folder path: ").strip().strip('"')
    recursive = input("🔁 Include subfolders? (y/n): ").lower() == "y"
    resize = input("📏 Resize images to A4? (y/n): ").lower() == "y"
    dpi_input = input("🎚️ Enter DPI (default 150): ").strip()
    name_input = input("📄 Output PDF name (without .pdf): ").strip()

    dpi = int(dpi_input) if dpi_input.isdigit() else 150
    name = name_input if name_input else "merged_output"
    output_path = os.path.join(path, f"{name}.pdf")

    if os.path.isdir(path):
        imgs = collect_images(path, recursive=recursive, resize=resize)
        create_pdf(imgs, output_path=output_path, dpi=dpi)
    else:
        print("❌ Invalid folder path.")
