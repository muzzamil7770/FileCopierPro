from PySide6.QtCore import QObject, Signal, QThread
from core.task import FileTask
from core.file_engine import copy_file_with_progress, copy_folder_with_progress


class CopyWorker(QObject):
    progress = Signal(object)
    finished = Signal(object)
    error = Signal(object)

    def __init__(self, task: FileTask):
        super().__init__()
        self.task = task
        self.is_paused = False
        self.is_cancelled = False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        try:
            if self.task.is_folder:
                copy_folder_with_progress(self.task, self.progress.emit)
            else:
                copy_file_with_progress(self.task, self.progress.emit)

            if self.is_cancelled:
                self.task.status = "cancelled"
            self.finished.emit(self.task)
        except Exception as e:
            self.task.status = "failed"
            self.task.error = str(e)
            self.error.emit(self.task)