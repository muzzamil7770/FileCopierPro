# ui/styles.py
STYLE = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}
QWidget {
    font-family: 'Segoe UI', Arial;
    font-size: 10pt;
}
QPushButton {
    padding: 10px 16px;
    border-radius: 6px;
    background-color: #0078d4;
    color: white;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #106ebe;
}
QListWidget {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
}
QProgressBar {
    border-radius: 4px;
    text-align: center;
    background-color: #3d3d3d;
}
QProgressBar::chunk {
    background-color: #00cc66;
    border-radius: 4px;
}
"""