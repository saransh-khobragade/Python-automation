import os
import shutil

def organize_files_into_folders():
    """
    Prompts the user for a directory path.
    For each file in that path, creates a folder with the same name (without extension)
    and moves the file into that folder.
    """
    path = input("Enter the directory path: ").strip()

    if not os.path.isdir(path):
        print(f"❌ Error: '{path}' is not a valid directory.")
        return

    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        # Only process files (skip folders)
        if os.path.isfile(item_path):
            file_name, _ = os.path.splitext(item)
            folder_path = os.path.join(path, file_name)

            # Create folder if it doesn't exist
            os.makedirs(folder_path, exist_ok=True)

            # Move the file into its folder
            shutil.move(item_path, os.path.join(folder_path, item))
            print(f"✅ Moved '{item}' → '{folder_path}/'")

if __name__ == "__main__":
    organize_files_into_folders()
