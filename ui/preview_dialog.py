from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
import os
from utils.formatter import human_size


class PreviewDialog(QDialog):
    def __init__(self, sources, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview & Select Items to Copy")
        self.resize(950, 620)
        self.sources = sources

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>{len(sources)} items detected</b>"))

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Type", "Size", "Path"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        for src in sources:
            item = QTreeWidgetItem()
            name = os.path.basename(src) or src
            is_dir = os.path.isdir(src)
            size_str = "Folder" if is_dir else human_size(os.path.getsize(src))

            item.setText(0, name)
            item.setText(1, "Folder" if is_dir else "File")
            item.setText(2, size_str)
            item.setText(3, src)
            item.setCheckState(0, Qt.CheckState.Checked)
            self.tree.addTopLevelItem(item)

        layout.addWidget(self.tree)

        btn_layout = QHBoxLayout()
        btn_select_all = QPushButton("Select All")
        btn_deselect = QPushButton("Deselect All")
        btn_copy = QPushButton("Start Copying Selected")
        btn_copy.setStyleSheet("background-color: #00cc66; font-weight: bold; padding: 8px;")

        btn_layout.addWidget(btn_select_all)
        btn_layout.addWidget(btn_deselect)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_copy)

        layout.addLayout(btn_layout)

        btn_select_all.clicked.connect(self.select_all)
        btn_deselect.clicked.connect(self.deselect_all)
        btn_copy.clicked.connect(self.accept)

    def select_all(self):
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setCheckState(0, Qt.CheckState.Checked)

    def deselect_all(self):
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setCheckState(0, Qt.CheckState.Unchecked)

    def get_selected(self):
        selected = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                selected.append(item.text(3))
        return selected