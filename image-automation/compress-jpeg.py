import os
import sys
import subprocess

# 📦 Auto-install Pillow if missing
try:
    from PIL import Image
except ImportError:
    print("📦 Pillow not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image

def compress_to_target(input_path, output_path=None, target_size=1024 * 1024):
    if not os.path.isfile(input_path):
        print("❌ File not found.")
        return

    if not input_path.lower().endswith((".jpg", ".jpeg")):
        print("❌ Only JPEG files are supported.")
        return

    if not output_path:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_compressed.jpg"

    try:
        img = Image.open(input_path)
    except Exception as e:
        print(f"❌ Failed to open image: {e}")
        return

    if img.mode != 'RGB':
        img = img.convert('RGB')

    min_q, max_q = 5, 95
    best_quality = None
    temp_file = output_path + ".temp.jpg"

    while min_q <= max_q:
        q = (min_q + max_q) // 2
        img.save(temp_file, format="JPEG", quality=q, optimize=True)
        size = os.path.getsize(temp_file)
        print(f"🔍 Trying quality {q}: {size / 1024:.2f} KB")

        if size <= target_size:
            best_quality = q
            min_q = q + 1
        else:
            max_q = q - 1

    if best_quality:
        img.save(output_path, format="JPEG", quality=best_quality, optimize=True)
        os.remove(temp_file)
        final_size = os.path.getsize(output_path) / 1024
        print(f"\n✅ Saved: {output_path} ({final_size:.2f} KB) at quality {best_quality}")
    else:
        print("❌ Could not compress below target size.")
        os.remove(temp_file)

# 🏃 Main runner
if __name__ == "__main__":
    input_file = input("📷 Enter path to JPEG file: ").strip().strip('"')

    size_mb = input("📦 Max output size in MB (default: 1): ").strip()
    try:
        target_bytes = int(float(size_mb) * 1024 * 1024) if size_mb else 1024 * 1024
    except:
        print("❌ Invalid size input, defaulting to 1 MB.")
        target_bytes = 1024 * 1024

    compress_to_target(input_file, target_size=target_bytes)
