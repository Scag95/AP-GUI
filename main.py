import sys
from PyQt6.QtWidgets import QApplication, QMainWindow,QLabel,QVBoxLayout,QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AP-GUI")
        self.resize(1200,800) #Tamaño de la ventana

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Un texto de prueba
        label = QLabel("Bienvenido al entorno de cálculo")
        layout.addWidget(label)
        # Aquí añadiremos luego el área de dibujo y barras de herramientas
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()


