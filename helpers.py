import os
import shutil


def copy_folder_recursive(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)

    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        target_root = os.path.join(dst, rel_path)

        os.makedirs(target_root, exist_ok=True)

        for file in files:
            shutil.copy2(
                os.path.join(root, file),
                os.path.join(target_root, file)
            )


def sync_folders(src, dst):
    src_files = set(os.listdir(src))
    dst_files = set(os.listdir(dst))

    to_copy = src_files - dst_files
    to_delete = dst_files - src_files

    return to_copy, to_delete