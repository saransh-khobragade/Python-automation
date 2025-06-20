import os

LOG_FILE = ".suffix_rename_log.txt"

def add_suffix_to_items(path, suffix):
    items = sorted(os.listdir(path), reverse=True)
    log_lines = []

    for item in items:
        old_path = os.path.join(path, item)

        # Skip if already has suffix
        if item.endswith(suffix):
            continue

        name, ext = os.path.splitext(item)
        if os.path.isfile(old_path):
            new_name = f"{name}{suffix}{ext}"
        else:
            new_name = f"{item} {suffix}"  # for folders

        new_path = os.path.join(path, new_name)

        try:
            os.rename(old_path, new_path)
            log_lines.append(f"{new_name}|{item}")
            print(f"✅ Renamed: '{item}' → '{new_name}'")
        except Exception as e:
            print(f"❌ Failed to rename '{item}': {e}")

    if log_lines:
        with open(os.path.join(path, LOG_FILE), "w") as f:
            f.write("\n".join(log_lines))
        print(f"\n📝 Rename log saved to '{LOG_FILE}'")
    else:
        print("ℹ️ No items were renamed.")

def undo_renames(path):
    log_path = os.path.join(path, LOG_FILE)

    if not os.path.exists(log_path):
        print("❌ No rename log found.")
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

    action = input("Type 'undo' to revert last rename, or press Enter to add suffix: ").strip().lower()

    if action == "undo":
        undo_renames(path)
    else:
        suffix = input("Enter the suffix to add (e.g., '_old'): ").strip()
        add_suffix_to_items(path, suffix)

if __name__ == "__main__":
    main()
