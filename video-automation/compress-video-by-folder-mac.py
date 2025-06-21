import os
import subprocess
from tqdm import tqdm

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}

def is_video_file(filename):
    return os.path.splitext(filename)[1].lower() in VIDEO_EXTENSIONS

def get_video_duration(input_path):
    """Return video duration in seconds"""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None

def compress_video(input_path, output_path):
    duration = get_video_duration(input_path)
    if not duration:
        print(f"⚠️ Skipping (could not determine duration): {input_path}")
        return

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "hevc_videotoolbox",  # Use Apple Silicon hardware encoder
        "-q:v", "30",                 # Better visual quality (lower = better)
        "-pix_fmt", "yuv420p",        # Wide compatibility
        "-tag:v", "hvc1",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-progress", "pipe:1",        # Stream progress
        "-nostats",
        "-y",
        output_path
    ]

    print(f"\n🎞 Compressing: {os.path.basename(input_path)}")
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    pbar = tqdm(total=duration, unit="s", dynamic_ncols=True, desc=os.path.basename(input_path))

    try:
        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.strip().split('=')[1])
                    seconds = ms / 1_000_000
                    pbar.n = min(int(seconds), int(duration))
                    pbar.refresh()
                except ValueError:
                    continue
        process.wait()
        pbar.n = int(duration)
        pbar.refresh()
        pbar.close()

        if process.returncode == 0:
            print(f"✅ Saved to: {output_path}\n")
        else:
            print(f"❌ Compression failed for: {input_path}\n")
    except Exception as e:
        print(f"Error during compression: {e}")
        process.kill()
        pbar.close()

def compress_videos_in_directory(directory):
    if not os.path.isdir(directory):
        print(f"❌ Invalid directory: {directory}")
        return

    compressed_dir = os.path.join(directory, "compressed")
    os.makedirs(compressed_dir, exist_ok=True)

    video_files = [f for f in os.listdir(directory) if is_video_file(f)]
    if not video_files:
        print("📁 No video files found.")
        return

    for filename in video_files:
        input_path = os.path.join(directory, filename)
        name, _ = os.path.splitext(filename)
        output_filename = f"{name}_compressed.mp4"
        output_path = os.path.join(compressed_dir, output_filename)
        compress_video(input_path, output_path)

if __name__ == "__main__":
    folder = input("Enter the path to the folder with videos: ").strip()
    compress_videos_in_directory(folder)
