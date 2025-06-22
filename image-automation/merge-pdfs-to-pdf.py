import os
import sys
import subprocess

# Auto-install PyPDF2
try:
    from PyPDF2 import PdfMerger
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    from PyPDF2 import PdfMerger

def collect_pdfs(folder_path, recursive=False):
    pdf_files = []
    for root, _, files in os.walk(folder_path):
        for f in sorted(files):
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))
        if not recursive:
            break
    return pdf_files

def merge_pdfs(pdf_list, output_path):
    if not pdf_list:
        print("❌ No PDF files found.")
        return

    merger = PdfMerger()
    for pdf in pdf_list:
        try:
            merger.append(pdf)
            print(f"➕ Added: {pdf}")
        except Exception as e:
            print(f"⚠️ Skipped {pdf}: {e}")

    merger.write(output_path)
    merger.close()
    print(f"\n✅ Merged PDF saved to: {output_path}")

if __name__ == "__main__":
    path = input("📁 Enter folder path with PDFs: ").strip().strip('"')

    if not os.path.isdir(path):
        print("❌ Invalid folder path.")
        sys.exit(1)

    recursive = input("🔁 Include subfolders? (y/n): ").strip().lower() == 'y'
    output_file = os.path.join(path, "merged_output.pdf")

    pdfs = collect_pdfs(path, recursive=recursive)
    merge_pdfs(pdfs, output_file)
