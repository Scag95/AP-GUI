from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal, Qt

class CommandLineWidget(QWidget):
    commandEntered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0) # Sin márgenes externos
        self.layout.setSpacing(0) 

        # 2. Línea de entrada
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Escribe un comando...")
        # Input ligeramente más claro para diferenciar
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: rgba(45, 45, 45, 180); 
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-weight: bold;
                border: none;
                border-top: 1px solid #3e3e3e;
                padding: 4px;
            }
        """)
        self.input_line.returnPressed.connect(self._on_enter)
        self.layout.addWidget(self.input_line)
        # Altura fija pequeña
        self.setFixedHeight(40)

    def _on_enter(self):
        cmd = self.input_line.text().strip()
        if cmd:
            self.commandEntered.emit(cmd)
            self.input_line.clear()

    def log_message(self, message, color='black', bold=False):
        # Método stub para no romper main_window, pero ya no hace nada visual
        print(f"[CMD LOG] {message}") 