import os
import sys
import subprocess

# Auto-install dependencies
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
COMMON_IMAGE_FORMATS = (
    '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif', '.heic', '.avif'
)
RAW_FORMATS = (
    '.cr2', '.nef', '.arw', '.orf', '.rw2', '.dng', '.raf', '.sr2', '.pef', '.raw'
)
SUPPORTED_FORMATS = COMMON_IMAGE_FORMATS + RAW_FORMATS

def convert_raw_to_jpeg(input_path, output_path):
    try:
        with rawpy.imread(input_path) as raw:
            rgb = raw.postprocess()
            imageio.imsave(output_path, rgb)
            print(f"✅ RAW converted: {input_path} → {output_path}")
    except Exception as e:
        print(f"❌ RAW conversion failed for {input_path}: {e}")

def convert_to_jpeg(input_path, output_dir=None):
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        print(f"❌ Skipping unsupported: {input_path}")
        return

    base = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir or os.path.dirname(input_path), f"{base}.jpg")

    if ext in RAW_FORMATS:
        convert_raw_to_jpeg(input_path, output_path)
        return

    try:
        img = Image.open(input_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(output_path, format='JPEG', quality=95)
        print(f"✅ Converted: {input_path} → {output_path}")
    except UnidentifiedImageError:
        print(f"⚠️ Unreadable image: {input_path}")
    except Exception as e:
        print(f"❌ Error converting {input_path}: {e}")

def convert_folder(path, recursive=False):
    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            convert_to_jpeg(full_path)
        if not recursive:
            break

if __name__ == "__main__":
    target_path = input("📂 Enter file or folder path: ").strip().strip('"')
    recursive = input("🔁 Search subfolders? (y/n): ").strip().lower() == 'y'

    if os.path.isdir(target_path):
        convert_folder(target_path, recursive=recursive)
    elif os.path.isfile(target_path):
        convert_to_jpeg(target_path)
    else:
        print("❌ Invalid path.")
