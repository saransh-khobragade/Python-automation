import subprocess
import json
import sys

def list_streams(file_path):
    print(f"📁 Checking file: {file_path}")
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-print_format", "json", file_path],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        streams = data.get("streams", [])
        if not streams:
            print("❌ No streams found.")
            return
        for s in streams:
            idx = s["index"]
            codec_type = s.get("codec_type", "unknown")
            codec_name = s.get("codec_name", "unknown")
            lang = s.get("tags", {}).get("language", "und")
            print(f"[{idx}] {codec_type.upper()} - {codec_name}, Lang: {lang}")
    except subprocess.CalledProcessError as e:
        print("❌ ffprobe failed:", e.stderr)
    except json.JSONDecodeError:
        print("❌ Could not parse ffprobe output.")
        print("Output was:", result.stdout)
    except Exception as e:
        print("❌ Unexpected error:", str(e))

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        list_streams(sys.argv[1])
    else:
        file_path = input("Enter media file path: ").strip('" ')
        list_streams(file_path)
