from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTextEdit
from PyQt6.QtCore import pyqtSignal

class CommandConsole(QWidget):
    commandEntered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.history = []
        self.history_index = 0

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        