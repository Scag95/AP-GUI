import sys
from PyQt6.QtWidgets import QApplication

#Importamos la clasee desde su ubicación en src/ui/
from src.ui.main_window import MainWindow

def main():
    # 1. Crear la apliación Qt 
    app = QApplication(sys.argv)

    #2 Instaciar la ventana principal
    window = MainWindow()
    window.show()

    #3 Entrar en el bucle de eventos
    sys.exit(app.exec())    

if __name__ == "__main__":
    main()
