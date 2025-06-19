import subprocess
import json
import os

def get_media_info(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Run ffprobe and get JSON output
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"ffprobe error: {result.stderr.strip()}")

        info = json.loads(result.stdout)
        return info

    except Exception as e:
        print(f"❌ Error reading media info: {e}")
        return None

def print_media_info(info):
    if not info:
        return

    print("\n📄 Format Info:")
    format_info = info.get('format', {})
    print(f"  Filename: {format_info.get('filename')}")
    print(f"  Duration: {format_info.get('duration')} seconds")
    print(f"  Size: {format_info.get('size')} bytes")
    print(f"  Format: {format_info.get('format_name')}")
    print(f"  Bitrate: {format_info.get('bit_rate')} bps")

    print("\n🎞️ Stream Info:")
    for i, stream in enumerate(info.get('streams', [])):
        print(f"\n  Stream #{i}:")
        print(f"    Codec Type: {stream.get('codec_type')}")
        print(f"    Codec Name: {stream.get('codec_name')}")
        print(f"    Codec Long Name: {stream.get('codec_long_name')}")
        if stream.get('codec_type') == 'video':
            print(f"    Resolution: {stream.get('width')}x{stream.get('height')}")
            print(f"    Frame Rate: {stream.get('avg_frame_rate')}")
        elif stream.get('codec_type') == 'audio':
            print(f"    Channels: {stream.get('channels')}")
            print(f"    Sample Rate: {stream.get('sample_rate')}")
        if 'language' in stream.get('tags', {}):
            print(f"    Language: {stream['tags']['language']}")

if __name__ == "__main__":
    file_path = input("🎥 Enter path to video file: ").strip()
    media_info = get_media_info(file_path)
    print_media_info(media_info)
