import subprocess
import os

def convert_video_to_mp3(input_path, output_path=None):
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    # Set output file path if not provided
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".mp3"

    # FFmpeg command for highest quality MP3 (320 kbps CBR)
    command = [
        "ffmpeg",
        "-i", input_path,           # Input file
        "-vn",                      # Remove video
        "-c:a", "libmp3lame",       # Use LAME MP3 encoder
        "-b:a", "320k",             # Set audio bitrate to 320 kbps
        "-ac", "2",                 # Ensure stereo
        "-ar", "44100",             # Sample rate 44.1kHz (CD quality)
        output_path
    ]

    print(f"\nConverting:\n{input_path} \n→ {output_path}\n")
    subprocess.run(command, check=True)
    print("✅ Conversion complete!")

# Example usage
if __name__ == "__main__":
    input_video = input("Enter full path to video file: ").strip()
    convert_video_to_mp3(input_video)
