import os
import sys
import subprocess

# Auto-install required modules
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
RAW_FORMATS = ('.cr2', '.nef', '.arw', '.dng', '.orf', '.rw2', '.raf', '.sr2', '.pef', '.raw')
COMMON_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif', '.heic', '.avif')
ALL_FORMATS = COMMON_FORMATS + RAW_FORMATS

def convert_raw_to_image(path):
    try:
        with rawpy.imread(path) as raw:
            rgb = raw.postprocess()
            return Image.fromarray(rgb)
    except Exception as e:
        print(f"❌ RAW error: {path} — {e}")
        return None

def convert_image_to_pdf(input_path):
    ext = os.path.splitext(input_path)[1].lower()
    base = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(os.path.dirname(input_path), f"{base}.pdf")

    try:
        if ext in RAW_FORMATS:
            image = convert_raw_to_image(input_path)
        else:
            image = Image.open(input_path)

        if image is None:
            print(f"❌ Skipping: {input_path}")
            return

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.save(output_path, "PDF", resolution=150.0)
        print(f"✅ PDF saved: {output_path}")
    except UnidentifiedImageError:
        print(f"⚠️ Unreadable image: {input_path}")
    except Exception as e:
        print(f"❌ Error converting {input_path}: {e}")

def convert_folder(folder_path, include_subfolders=False):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(ALL_FORMATS):
                convert_image_to_pdf(os.path.join(root, file))
        if not include_subfolders:
            break

# === Main ===
if __name__ == "__main__":
    path = input("📂 Enter image file or folder path: ").strip().strip('"')

    if os.path.isfile(path):
        convert_image_to_pdf(path)

    elif os.path.isdir(path):
        subfolders = input("🔁 Include subfolders? (y/n): ").strip().lower() == 'y'
        convert_folder(path, include_subfolders=subfolders)

    else:
        print("❌ Invalid path. Please enter a valid image file or folder.")
