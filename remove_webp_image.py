import os
import sys

def remove_webp_files(base_folder):
    deleted_files = []

    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith((".webp", ".webpg")):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    print("\n Done!")
    print(f"Total files deleted: {len(deleted_files)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python3 script.py <assets_folder_path>")
        sys.exit(1)

    assets_path = sys.argv[1]

    if not os.path.exists(assets_path):
        print("❌ Path does not exist!")
        sys.exit(1)

    remove_webp_files(assets_path)