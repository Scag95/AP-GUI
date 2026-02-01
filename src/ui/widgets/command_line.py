from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal, Qt
from src.ui.widgets.unit_selector import UnitSelectorWidget

class CommandLineWidget(QWidget):
    commandEntered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setStyleSheet("background: transparent;")
        
        # Layout Horizontal (Input + Selector)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2) 

        # 1. Línea de entrada
        self.input_line = QLineEdit()
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
            self.commandEntered.emit(cmd)
            self.input_line.clear()

    def log_message(self, message, color='black', bold=False):
        # Log a consola (stdout), la UI ya no muestra logs superpuestos para mantener limpieza
        prefix = "[ERROR]" if color == "red" else "[INFO]"
        print(f"{prefix} {message}")
 