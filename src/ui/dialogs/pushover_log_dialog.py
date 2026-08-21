from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QApplication


class PushoverLogDialog(QDialog):
    """Diálogo para visualizar los logs guardados del último análisis Pushover."""

    def __init__(self, log_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logs del Análisis Pushover")
        self.resize(700, 500)

        # Centrar
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(log_text)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #3e3e3e;
                padding: 6px;
            }
        """)
        layout.addWidget(self.text_edit)

        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
