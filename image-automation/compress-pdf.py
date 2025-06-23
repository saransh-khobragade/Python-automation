import os
import sys
import subprocess
import io

# Auto-install PyMuPDF and Pillow
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

def compress_pdf(input_path, output_path=None, image_quality=70, scale=0.5, remove_metadata=True):
    if not os.path.isfile(input_path):
        print("❌ File not found.")
        return

    if not input_path.lower().endswith(".pdf"):
        print("❌ Only PDF files are supported.")
        return

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + "_compressed.pdf"

    print(f"📥 Opening: {input_path}")
    doc = fitz.open(input_path)
    new_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)

        # Convert pixmap to PIL image
        mode = "RGB" if pix.alpha == 0 else "RGBA"
        image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        # Save image to memory buffer with quality
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="JPEG", quality=image_quality, optimize=True)
        img_buffer.seek(0)

        # Insert image into new PDF
        img_rect = fitz.Rect(0, 0, pix.width, pix.height)
        new_page = new_doc.new_page(width=pix.width, height=pix.height)
        new_page.insert_image(img_rect, stream=img_buffer.read())

        print(f"📄 Compressed page {page_num+1}/{len(doc)}")

    if remove_metadata:
        new_doc.set_metadata({})

    new_doc.save(output_path)
    doc.close()
    new_doc.close()

    final_size = os.path.getsize(output_path) / 1024
    print(f"\n✅ Compressed PDF saved: {output_path} ({final_size:.2f} KB)")

if __name__ == "__main__":
    input_pdf = input("📂 Enter path to PDF: ").strip().strip('"')

    quality_input = input("🎚️ JPEG quality (10–95, default 70): ").strip()
    try:
        quality = int(quality_input) if quality_input else 70
        if not (10 <= quality <= 95): raise ValueError
    except:
        print("⚠️ Invalid input. Using default quality: 70.")
        quality = 70

    scale_input = input("📏 Scale (0.3–1.0, default 0.5): ").strip()
    try:
        scale = float(scale_input) if scale_input else 0.5
        if not (0.1 <= scale <= 1.0): raise ValueError
    except:
        print("⚠️ Invalid scale. Using 0.5.")
        scale = 0.5

    compress_pdf(input_pdf, image_quality=quality, scale=scale)
