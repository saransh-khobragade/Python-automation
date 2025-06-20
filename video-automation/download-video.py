import subprocess

def download_youtube_video(url, output_dir="."):
    try:
        print(f"📥 Downloading: {url}")
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",
            "-o", f"{output_dir}/%(title)s.%(ext)s",
            url
        ], check=True)
        print("✅ Download complete.")
    except subprocess.CalledProcessError as e:
        print(f"❌ yt-dlp failed: {e}")

if __name__ == "__main__":
    url = input("Enter video URL: ").strip()
    download_youtube_video(url)
