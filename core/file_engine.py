import os
import shutil
from datetime import datetime
from core.task import FileTask


def copy_file_with_progress(task: FileTask, progress_callback):
    if not os.path.isfile(task.src):
        return
    file_size = os.path.getsize(task.src)
    copied = 0
    buffer_size = 1024 * 1024  # 1MB

    task.started_at = datetime.now()
    task.status = "copying"

    dst_file = os.path.join(task.dst, os.path.basename(task.src))

    with open(task.src, 'rb') as fsrc, open(dst_file, 'wb') as fdst:
        while True:
            chunk = fsrc.read(buffer_size)
            if not chunk:
                break
            fdst.write(chunk)
            copied += len(chunk)

            percent = (copied / file_size) * 100
            elapsed = (datetime.now() - task.started_at).total_seconds()
            speed = copied / elapsed if elapsed > 0 else 0
            eta = (file_size - copied) / speed if speed > 0 else 0

            task.progress = percent
            task.copied_size = copied
            task.speed = speed
            task.eta = eta

            progress_callback(task)

    task.status = "done"
    task.completed_at = datetime.now()
    task.progress = 100.0
    progress_callback(task)


def copy_folder_with_progress(task: FileTask, progress_callback):
    if not os.path.isdir(task.src):
        return

    task.started_at = datetime.now()
    task.status = "copying"

    dst_folder = os.path.join(task.dst, os.path.basename(task.src))

    total_size = task.size
    copied = 0

    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    for root, dirs, files in os.walk(task.src):
        rel_path = os.path.relpath(root, task.src)
        target_root = os.path.join(dst_folder, rel_path)
        os.makedirs(target_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_root, file)

            file_size = os.path.getsize(src_file)
            shutil.copy2(src_file, dst_file)

            copied += file_size
            percent = (copied / total_size) * 100 if total_size > 0 else 100

            elapsed = (datetime.now() - task.started_at).total_seconds()
            speed = copied / elapsed if elapsed > 0 else 0
            eta = (total_size - copied) / speed if speed > 0 else 0

            task.progress = percent
            task.copied_size = copied
            task.speed = speed
            task.eta = eta

            progress_callback(task)

    task.status = "done"
    task.completed_at = datetime.now()
    task.progress = 100.0
    progress_callback(task)