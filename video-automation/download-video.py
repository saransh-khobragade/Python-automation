import subprocess
import os
import shutil
import sys

def is_tool_available(name):
    return shutil.which(name) is not None

def download_video(url, output_dir="."):
    if not is_tool_available("yt-dlp"):
        print("❌ 'yt-dlp' is not installed or not in PATH.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    try:
        print(f"📥 Downloading: {url}")
        result = subprocess.run([
            "yt-dlp",
            "--restrict-filenames",
            "--print", "after_move:filepath",  # get actual saved filename
            "-f", "bestvideo+bestaudio/best",
            "-o", f"{output_dir}/%(title)s.%(ext)s",
            url
        ], capture_output=True, text=True, check=True)

        downloaded_file = result.stdout.strip()
        print(f"✅ Download complete: {downloaded_file}")
        return downloaded_file

    except subprocess.CalledProcessError as e:
        print(f"❌ yt-dlp failed: {e}")
        return None

def convert_to_mp4(input_path, delete_original=False):
    if not input_path or not os.path.exists(input_path):
        print("❌ Input file not found for conversion.")
        return None

    if not is_tool_available("ffmpeg"):
        print("❌ 'ffmpeg' is not installed or not in PATH.")
        sys.exit(1)

    base, ext = os.path.splitext(input_path)
    output_path = base + ".mp4"

    if ext.lower() == ".mp4":
        print("🟢 Already in MP4 format. No conversion needed.")
        return input_path

    try:
        print("🎞️ Converting to MP4...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", "libx265",
            "-preset", "fast",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path
        ], check=True)

        print(f"✅ Converted to: {output_path}")

        if delete_original:
            os.remove(input_path)
            print(f"🧹 Deleted original file: {input_path}")

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"❌ ffmpeg conversion failed: {e}")
        return None

if __name__ == "__main__":
    url = input("🔗 Enter  video URL: ").strip()
    output_dir = input("📁 Enter output folder (or press Enter for current): ").strip() or "."

    downloaded_file = download_video(url, output_dir)
    if downloaded_file:
        convert_to_mp4(downloaded_file, delete_original=True)  # Set False if you want to keep original
