import subprocess
import os
from tqdm import tqdm

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}

def get_video_duration(input_path):
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                input_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        duration_str = result.stdout.strip()
        if not duration_str or duration_str == 'N/A':
            raise ValueError("ffprobe could not determine video duration.")
        return float(duration_str)
    except Exception as e:
        raise RuntimeError(f"Failed to get video duration: {e}")

def compress_video(input_path, crf="23", preset="slow"):
    if not os.path.isfile(input_path):
        print(f"⚠️ File not found: {input_path}")
        return

    input_dir = os.path.dirname(input_path)
    input_filename = os.path.basename(input_path)
    name, _ = os.path.splitext(input_filename)
    output_filename = f"{name}_compressed.mp4"  # Force .mp4 output
    output_path = os.path.join(input_dir, output_filename)

    try:
        total_duration = get_video_duration(input_path)
    except RuntimeError as e:
        print(f"❌ Skipping '{input_filename}': {e}")
        return

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libx265",
        "-preset", preset,
        "-x265-params", "profile=main",
        "-crf", crf,
        "-c:a", "copy",         # Copy audio without re-encoding
        "-y",
        "-progress", "pipe:1",
        "-nostats",
        output_path
    ]

    print(f"\n🔄 Compressing: {input_filename} with CRF={crf}, preset={preset}")
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    pbar = tqdm(total=total_duration, unit='s', desc=name, dynamic_ncols=True)

    try:
        for line in process.stdout:
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.strip().split('=')[1])
                    seconds = ms / 1_000_000
                    pbar.n = min(int(seconds), int(total_duration))
                    pbar.refresh()
                except ValueError:
                    continue
        process.wait()
        pbar.n = int(total_duration)
        pbar.refresh()
        pbar.close()

        if process.returncode == 0:
            print(f"✅ Saved to: {output_path}")
        else:
            print(f"❌ ffmpeg error on {input_filename} (code {process.returncode})")

    except Exception as e:
        print(f"❌ Error during compression of {input_filename}: {e}")
        process.kill()
        pbar.close()

def batch_compress(folder_path, crf="23", preset="slow"):
    if not os.path.isdir(folder_path):
        print(f"❌ Invalid folder path: {folder_path}")
        return

    video_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS
    ]

    if not video_files:
        print("📂 No video files found in the folder.")
        return

    print(f"\n📁 Found {len(video_files)} video(s) to compress.\n")
    for video in video_files:
        compress_video(video, crf, preset)

if __name__ == "__main__":
    print("\n🎬 Batch Video Compressor (HEVC Encoding, audio copied, CRF control)\n")

    folder = input("📁 Enter the folder path containing video files: ").strip()

    crf = input("🎚 Enter CRF value (18-28, lower=better quality) [default: 23]: ").strip()
    if not crf or not crf.isdigit():
        crf = "23"
    else:
        crf_int = int(crf)
        if crf_int < 18 or crf_int > 28:
            print("⚠️ CRF out of range, defaulting to 23.")
            crf = "23"

    valid_presets = {"ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"}
    preset = input("⚙️ Enter encoding preset (ultrafast, fast, medium, slow, veryslow) [default: slow]: ").strip().lower()
    if preset not in valid_presets:
        print("⚠️ Invalid or empty preset, defaulting to 'slow'.")
        preset = "slow"

    batch_compress(folder, crf, preset)
