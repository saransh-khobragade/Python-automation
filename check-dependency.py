import importlib.util
import subprocess
import sys

# List your required pip packages here
REQUIRED_PACKAGES = {
    "yt-dlp": "yt-dlp",
    "ffmpeg": "ffmpeg-python",  # This installs the Python wrapper; assumes ffmpeg binary is already installed
}

def check_and_install_packages():
    for module_name, package_name in REQUIRED_PACKAGES.items():
        if importlib.util.find_spec(module_name) is None:
            print(f"📦 '{module_name}' not found. Installing '{package_name}'...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        else:
            print(f"✅ '{module_name}' is already installed.")

if __name__ == "__main__":
    check_and_install_packages()
