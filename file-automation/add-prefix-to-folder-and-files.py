import os

LOG_FILE = ".rename_log.txt"

def add_prefix_to_items(path, prefix):
    items = sorted(os.listdir(path), reverse=True)
    log_lines = []

    for item in items:
        old_path = os.path.join(path, item)

        # Skip if already has the prefix
        if item.startswith(f"{prefix}-"):
            continue

        new_name = f"{prefix}-{item}"
        new_path = os.path.join(path, new_name)

        try:
            os.rename(old_path, new_path)
            log_lines.append(f"{new_name}|{item}")  # Log: new_name|old_name
            print(f"✅ Renamed: '{item}' → '{new_name}'")
        except Exception as e:
            print(f"❌ Failed to rename '{item}': {e}")

    # Write the log file if any renames happened
    if log_lines:
        with open(os.path.join(path, LOG_FILE), "w") as f:
            f.write("\n".join(log_lines))
        print(f"\n📝 Rename log saved to '{LOG_FILE}' in the folder.")
    else:
        print("ℹ️ No files or folders were renamed.")

def undo_renames(path):
    log_path = os.path.join(path, LOG_FILE)

    if not os.path.exists(log_path):
        print("❌ No rename log found to undo.")
        return

    with open(log_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        new_name, old_name = line.strip().split("|")
        new_path = os.path.join(path, new_name)
        old_path = os.path.join(path, old_name)

        try:
            os.rename(new_path, old_path)
            print(f"↩️ Undone: '{new_name}' → '{old_name}'")
        except Exception as e:
            print(f"❌ Failed to undo '{new_name}': {e}")

    os.remove(log_path)
    print(f"\n🗑️ Removed log file '{LOG_FILE}'")

def main():
    path = input("Enter the directory path: ").strip()
    if not os.path.isdir(path):
        print(f"❌ Error: '{path}' is not a valid directory.")
        return

    action = input("Type 'undo' to revert last rename, or press Enter to add prefix: ").strip().lower()

    if action == "undo":
        undo_renames(path)
    else:
        prefix = input("Enter the prefix to add (e.g., 'demo'): ").strip()
        add_prefix_to_items(path, prefix)

if __name__ == "__main__":
    main()
