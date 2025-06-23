import os
import sys
import subprocess

# 📦 Auto-install PyMuPDF and Pillow if missing
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import fitz  # PyMuPDF
except ImportError:
    print("📦 Installing PyMuPDF...")
    install("pymupdf")
    import fitz

try:
    from PIL import Image
except ImportError:
    print("📦 Installing Pillow...")
    install("pillow")
    from PIL import Image

def convert_pdf_to_jpeg_native(pdf_path, zoom=2.0, quality=95):
    if not os.path.isfile(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    output_folder = os.path.dirname(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    print(f"📄 Opening: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)  # 2.0 = ~300 DPI
        pix = page.get_pixmap(matrix=mat)

        output_file = os.path.join(output_folder, f"{base_name}_page_{page_num+1}.jpg")
        pix.save(output_file, "jpeg")
        print(f"✅ Saved: {output_file}")

    print(f"✅ Finished converting {total_pages} pages.")
    doc.close()

if __name__ == "__main__":
    input_path = input("📥 Enter full path to PDF file: ").strip().strip('"')
    convert_pdf_to_jpeg_native(input_path)
