import os
import sys
import subprocess
import tempfile
import shutil

# Auto-install required packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import fitz  # PyMuPDF
except ImportError:
    install("pymupdf")
    import fitz

try:
    from PIL import Image
except ImportError:
    install("pillow")
    from PIL import Image

# Convert PDF to JPEG images using PyMuPDF
def pdf_to_jpegs(pdf_path, output_folder, dpi=100):
    zoom = dpi / 72  # convert DPI to zoom factor
    doc = fitz.open(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    image_paths = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(output_folder, f"{base_name}_page_{page_num+1}.jpg")
        pix.save(img_path, "jpeg")
        image_paths.append(img_path)
        print(f"🖼️  Saved JPEG: {img_path}")

    doc.close()
    return image_paths

# Compress JPEGs to target size
def compress_jpeg_to_target(input_path, target_size=1024 * 1024):
    try:
        img = Image.open(input_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        min_q, max_q = 5, 95
        best_q = None
        temp_file = input_path + ".temp.jpg"

        while min_q <= max_q:
            q = (min_q + max_q) // 2
            img.save(temp_file, format="JPEG", quality=q, optimize=True)
            size = os.path.getsize(temp_file)

            if size <= target_size:
                best_q = q
                min_q = q + 1
            else:
                max_q = q - 1

        if best_q:
            img.save(input_path, format="JPEG", quality=best_q, optimize=True)
            os.remove(temp_file)
            print(f"✅ Compressed: {os.path.basename(input_path)} to {os.path.getsize(input_path) // 1024} KB at quality {best_q}")
        else:
            os.remove(temp_file)
            print(f"❌ Could not compress {input_path} under target size.")
    except Exception as e:
        print(f"❌ Error compressing {input_path}: {e}")

# Combine JPEGs into one PDF
def images_to_pdf(image_paths, output_pdf_path):
    images = []
    for path in image_paths:
        try:
            img = Image.open(path)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            images.append(img)
        except Exception as e:
            print(f"⚠️ Skipping unreadable image: {path} ({e})")

    if not images:
        print("❌ No valid images to save as PDF.")
        return

    first, rest = images[0], images[1:]
    first.save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=rest)
    print(f"\n📄 Final compressed PDF saved: {output_pdf_path}")

# Main runner
if __name__ == "__main__":
    input_pdf = input("📥 Enter path to PDF: ").strip().strip('"')
    if not os.path.isfile(input_pdf) or not input_pdf.lower().endswith('.pdf'):
        print("❌ Invalid PDF file.")
        sys.exit(1)

    # Target JPEG size input
    size_input = input("📦 Max JPEG size in MB (default: 1): ").strip()
    try:
        max_bytes = int(float(size_input) * 1024 * 1024) if size_input else 1024 * 1024
    except:
        print("❌ Invalid size input, using 1 MB.")
        max_bytes = 1024 * 1024

    # DPI input
    dpi_input = input("🖨️  DPI for rendering PDF (default: 100): ").strip()
    try:
        dpi = int(dpi_input) if dpi_input else 150
        if dpi < 72 or dpi > 600:
            raise ValueError
    except:
        print("❌ Invalid DPI input, using 100 DPI.")
        dpi = 100

    # Process
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\n📂 Temporary working folder: {temp_dir}")
        jpeg_paths = pdf_to_jpegs(input_pdf, temp_dir, dpi=dpi)

        for jpeg in jpeg_paths:
            compress_jpeg_to_target(jpeg, target_size=max_bytes)

        output_pdf = os.path.splitext(input_pdf)[0] + "_compressed.pdf"
        images_to_pdf(jpeg_paths, output_pdf)

    print("\n🧹 Temporary files cleaned up.")
