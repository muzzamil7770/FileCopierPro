import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QListWidget, QListWidgetItem, QFileDialog, QDialog
)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QFont

from core.task import FileTask
from core.worker import CopyWorker
from ui.preview_dialog import PreviewDialog
from utils.formatter import human_size, human_speed, human_eta


class MainWindow(QMainWindow):
    MAX_CONCURRENT = 4

    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Copier Pro 🚀")
        self.setGeometry(80, 80, 1150, 740)
        self.setStyleSheet(self.get_dark_style())

        self.tasks = []
        self.workers = {}      # task_id -> worker
        self.threads = {}      # task_id -> thread
        self.active_count = 0

        self.init_ui()

    def get_dark_style(self):
        return """
        QMainWindow, QWidget { background-color: #1e1e1e; color: #eeeeee; }
        QListWidget { background-color: #2d2d2d; border: 1px solid #555; border-radius: 8px; padding: 4px; }
        QProgressBar { border: 1px solid #555; border-radius: 6px; text-align: center; background: #3d3d3d; height: 18px; }
        QProgressBar::chunk { background-color: #00cc88; border-radius: 5px; }
        QPushButton { padding: 10px 18px; border-radius: 6px; font-weight: bold; }
        QPushButton#primary { background-color: #0078d4; }
        QPushButton#primary:hover { background-color: #106ebe; }
        """

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("File Copier Pro 🚀")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        main_layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add Files / Folders")
        self.btn_add.clicked.connect(self.add_sources)

        self.btn_start = QPushButton("▶ Start All")
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self.start_all)

        self.btn_pause_all = QPushButton("⏸ Pause All")
        self.btn_pause_all.clicked.connect(self.pause_all)

        self.btn_resume_all = QPushButton("▶ Resume All")
        self.btn_resume_all.clicked.connect(self.resume_all)

        self.btn_cancel_all = QPushButton("✕ Cancel All")
        self.btn_cancel_all.clicked.connect(self.cancel_all)

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_start)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_pause_all)
        toolbar.addWidget(self.btn_resume_all)
        toolbar.addWidget(self.btn_cancel_all)
        main_layout.addLayout(toolbar)

        self.task_list = QListWidget()
        main_layout.addWidget(self.task_list)

        self.overall_label = QLabel("Overall Progress: 0% (0/0)")
        self.overall_progress = QProgressBar()
        main_layout.addWidget(self.overall_label)
        main_layout.addWidget(self.overall_progress)

    def add_sources(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", options=QFileDialog.ShowDirsOnly)

        sources = files[:]
        if folder:
            sources.append(folder)

        if not sources:
            return

        dialog = PreviewDialog(sources, self)
        if dialog.exec() == QDialog.Accepted:
            selected = dialog.get_selected()
            if not selected:
                return

            dest = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
            if not dest:
                return

            for src in selected:
                task = FileTask(src=src, dst=dest)
                self.tasks.append(task)
                self.add_task_to_list(task)

    def add_task_to_list(self, task):
        item = QListWidgetItem()
        item.setData(1000, task)
        self.update_task_item(item, task)
        self.task_list.addItem(item)

    def update_task_item(self, item, task):
        name = os.path.basename(task.src)
        size_str = human_size(task.size)
        speed_str = human_speed(task.speed)
        eta_str = human_eta(task.eta)
        text = f"{name}  |  {task.status.upper()}  |  {task.progress:.1f}%  |  {size_str}  |  {speed_str}  |  ETA: {eta_str}"
        item.setText(text)

    def get_task_id(self, task: FileTask) -> str:
        return f"{task.src}|{task.dst}"

    def start_all(self):
        for task in [t for t in self.tasks if t.status == "queued"]:
            if self.active_count < self.MAX_CONCURRENT:
                self.start_task(task)

    def start_task(self, task):
        if task.status not in ("queued", "paused", "failed"):
            return

        task.status = "copying"
        task_id = self.get_task_id(task)

        thread = QThread()
        worker = CopyWorker(task)

        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        worker.progress.connect(self.on_progress)
        worker.finished.connect(self.on_finished)
        worker.error.connect(self.on_error)

        self.workers[task_id] = worker
        self.threads[task_id] = thread
        self.active_count += 1

        thread.start()
        self.refresh_list()

    def on_progress(self, task):
        self.refresh_list()
        self.update_overall_progress()

    def on_finished(self, task):
        self.cleanup_task(task)
        self.refresh_list()
        self.update_overall_progress()
        self.start_next_queued()

    def on_error(self, task):
        self.cleanup_task(task)
        self.refresh_list()
        self.update_overall_progress()
        self.start_next_queued()

    def cleanup_task(self, task):
        task_id = self.get_task_id(task)
        if task_id in self.threads:
            self.threads[task_id].quit()
            self.threads[task_id].wait(500)
            self.threads.pop(task_id, None)
            self.workers.pop(task_id, None)
            self.active_count = max(0, self.active_count - 1)

    def start_next_queued(self):
        if self.active_count >= self.MAX_CONCURRENT:
            return
        for task in self.tasks:
            if task.status == "queued":
                self.start_task(task)
                break

    def pause_all(self):
        for worker in self.workers.values():
            worker.pause()
        for task in self.tasks:
            if task.status == "copying":
                task.status = "paused"
        self.refresh_list()

    def resume_all(self):
        for worker in self.workers.values():
            worker.resume()
        for task in self.tasks:
            if task.status == "paused":
                task.status = "copying"
        self.refresh_list()

    def cancel_all(self):
        for worker in list(self.workers.values()):
            worker.cancel()
        self.refresh_list()

    def refresh_list(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task = item.data(1000)
            if task:
                self.update_task_item(item, task)

    def update_overall_progress(self):
        if not self.tasks:
            return
        total = sum(t.progress for t in self.tasks) / len(self.tasks)
        done = sum(1 for t in self.tasks if t.status in ("done", "cancelled", "failed"))
        self.overall_label.setText(f"Overall Progress: {total:.1f}% ({done}/{len(self.tasks)})")
        self.overall_progress.setValue(int(total))