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

def compress_video(input_path, preset="slow", bitrate="1M", use_gpu=True, output_dir=None):
    if not os.path.isfile(input_path):
        print(f"File not found: {input_path}")
        return

    input_filename = os.path.basename(input_path)
    name, _ = os.path.splitext(input_filename)
    output_filename = f"{name}_compressed.mp4"

    if output_dir is None:
        output_dir = os.path.dirname(input_path)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    try:
        total_duration = get_video_duration(input_path)
    except RuntimeError as e:
        print(f"Skipping '{input_filename}': {e}")
        return

    ffmpeg_cmd = ["ffmpeg"]

    if use_gpu:
        ffmpeg_cmd += ["-hwaccel", "cuda"]

    ffmpeg_cmd += [
        "-i", input_path,
        "-c:v", "hevc_nvenc" if use_gpu else "libx265",
        "-preset", preset,
        "-rc", "vbr",
        "-cq", "19",
        "-b:v", bitrate,
        "-maxrate", "5M",
        "-bufsize", "10M",
        "-c:a", "aac",
        "-b:a", "192k",
        "-y",
        "-progress", "pipe:1",
        "-nostats",
        output_path
    ]

    print(f"Compressing: {input_filename} with compressed settings")
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
            print(f"Saved to: {output_path}")
        else:
            print(f"ffmpeg error on {input_filename} (code {process.returncode})")

    except Exception as e:
        print(f"Error during compression of {input_filename}: {e}")
        process.kill()
        pbar.close()

def batch_compress(folder_path, preset="slow", bitrate="1M", use_gpu=True):
    if not os.path.isdir(folder_path):
        print(f"Invalid folder path: {folder_path}")
        return

    video_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS
    ]

    if not video_files:
        print("No video files found in the folder.")
        return

    output_dir = os.path.join(folder_path, "compressed")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Found {len(video_files)} video(s) to compress.\n")
    for video in video_files:
        compress_video(video, preset, bitrate, use_gpu, output_dir)

if __name__ == "__main__":
    try:
        print("Batch Video Compressor (YouTube-Like HEVC Encoding)\n")

        folder = input("Enter the folder path containing video files: ").strip()

        valid_presets = {"default", "slow", "medium", "fast", "hq", "hp", "ll", "llhq", "llhp", "bd"}
        preset = input("Enter NVIDIA preset (default, slow, fast, hq, ll, etc.) [default: slow]: ").strip().lower()
        if preset not in valid_presets:
            print("Invalid or empty preset, defaulting to 'slow'.")
            preset = "slow"

        bitrate = input("Enter target video bitrate (e.g., 1M, 2M, 5M) [default: 1M]: ").strip()
        if not bitrate:
            bitrate = "1M"

        gpu_input = input("Use GPU acceleration with NVENC? (y/n) [default: y]: ").strip().lower()
        use_gpu = gpu_input != 'n'

        batch_compress(folder, preset, bitrate, use_gpu)
    except KeyboardInterrupt:
        print("Process interrupted by user.")
