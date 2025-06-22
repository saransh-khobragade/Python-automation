import os
import fitz  # PyMuPDF
from PIL import Image
import sys
import subprocess

# Auto-install dependencies
def auto_install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

try:
    import fitz
except ImportError:
    print("📦 Installing pymupdf...")
    auto_install("pymupdf")
    import fitz

try:
    from PIL import Image
except ImportError:
    print("📦 Installing pillow...")
    auto_install("pillow")
    from PIL import Image

def compress_pdf_as_images(input_path, output_path=None, dpi=100, quality=40):
    if not os.path.isfile(input_path):
        print("❌ File not found.")
        return

    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_compressed.pdf"

    doc = fitz.open(input_path)
    image_list = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Compress to JPEG in-memory
        temp = f"page_{page_number + 1}.jpg"
        img.save(temp, "JPEG", quality=quality)
        image_list.append(temp)

    # Rebuild PDF from compressed JPEGs
    pdf_images = [Image.open(img).convert("RGB") for img in image_list]
    pdf_images[0].save(output_path, save_all=True, append_images=pdf_images[1:])

    # Clean temp files
    for f in image_list:
        os.remove(f)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✅ Max-compressed PDF saved: {output_path} ({size_kb:.2f} KB)")

# 🏃 Run
if __name__ == "__main__":
    input_path = input("📄 Enter path to PDF: ").strip().strip('"')
    dpi = input("🖼️ Render DPI (default 100): ").strip()
    quality = input("📷 JPEG quality (1–100, default 40): ").strip()

    try:
        dpi = int(dpi) if dpi else 100
    except:
        dpi = 100

    try:
        quality = int(quality) if quality else 40
    except:
        quality = 40

    compress_pdf_as_images(input_path, dpi=dpi, quality=quality)
