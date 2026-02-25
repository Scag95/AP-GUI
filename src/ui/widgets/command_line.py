from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal, Qt
from src.ui.widgets.unit_selector import UnitSelectorWidget

class HistoryLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []
        self.history_index = 0
        self.temp_text = ""

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            if self.history_index > 0:
                if self.history_index == len(self.history):
                    self.temp_text = self.text()
                self.history_index -= 1
                self.setText(self.history[self.history_index])
        elif event.key() == Qt.Key.Key_Down:
            if self.history_index < len(self.history):
                self.history_index += 1
                if self.history_index == len(self.history):
                    self.setText(self.temp_text)
                else:
                    self.setText(self.history[self.history_index])
        else:
            super().keyPressEvent(event)

    def add_history(self, text):
        if text:
            # Add unless it's exactly the same as the last one
            if not self.history or self.history[-1] != text:
                self.history.append(text)
                if len(self.history) > 100:
                    self.history.pop(0)
            self.history_index = len(self.history)
            self.temp_text = ""

class CommandLineWidget(QWidget):
    commandEntered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Eliminada transparencia para uso en DockWidget
        self.setStyleSheet("background-color: #2D2D2D;")
        
        # Layout Horizontal (Input + Selector)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2) 

        # 1. Línea de entrada
        self.input_line = HistoryLineEdit()
        self.input_line.setPlaceholderText("Escribe un comando... (e.g., 'tag nodes on')")
        # Input style
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: rgba(45, 45, 45, 180); 
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-weight: bold;
                border: none;
                border-top: 1px solid #3e3e3e;
                padding: 4px;
                padding-left: 10px;
            }
        """)
        self.input_line.returnPressed.connect(self._on_enter)
        
        # Añadir con stretch para que ocupe todo el ancho disponible
        self.layout.addWidget(self.input_line, stretch=1)

        # 2. Selector de Unidades
        self.unit_selector = UnitSelectorWidget()
        self.layout.addWidget(self.unit_selector, stretch=0)

        # Altura fija pequeña
        self.setFixedHeight(40)

    def _on_enter(self):
        cmd = self.input_line.text().strip()
        if cmd:
            self.input_line.add_history(cmd)
            self.commandEntered.emit(cmd)
            self.input_line.clear()

    def log_message(self, message, color='black', bold=False):
        # Log a consola (stdout), la UI ya no muestra logs superpuestos para mantener limpieza
        prefix = "[ERROR]" if color == "red" else "[INFO]"
        print(f"{prefix} {message}")
 