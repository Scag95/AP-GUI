from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QPushButton, QWidget, QLabel,
                             QComboBox,QStackedWidget)

from src.ui.widgets.material_forms import ConcreteForm, SteelForm
from src.analysis.materials import Concrete01, Steel01

class MaterialDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Definir Materiales")
        self.resize(800,600)

        self.main_layout = QHBoxLayout(self)

        #Panel Izquierdo (Lista)
        self.left_panel_layout = QVBoxLayout()

        self.materials_list  = QListWidget()
        self.left_panel_layout.addWidget(self.materials_list )

        #Selector de tipo de material
        self.combo_type =QComboBox()
        self.combo_type.addItems(["Concrete01","Steel01"])
        self.left_panel_layout.addWidget(self.combo_type)

        #Botones de control
        self.btn_add = QPushButton("Añadir Material")
        self.btn_delete =QPushButton("Borrar Material")
        self.left_panel_layout.addWidget(self.btn_add)
        self.left_panel_layout.addWidget(self.btn_delete)

        #Añadimos panel izquierdo al layout principal
        self.main_layout.addLayout(self.left_panel_layout, stretch=1)

        #Panel Derecho
        self.right_panel_layout = QVBoxLayout()

        self.form_stack = QStackedWidget()

        #Creamos instancias en los formularios
        self.form_concrete = ConcreteForm()
        self.form_steel = SteelForm()

        #Los añadimos a la pila
        self.form_stack.addWidget(self.form_concrete)       #Indice 0
        self.form_stack.addWidget(self.form_steel)          #Indice 1

        self.right_panel_layout.addWidget(self.form_stack)
        #Añadimos el panel derefcho a layout principal
        self.main_layout.addLayout(self.right_panel_layout, stretch=2)
        
        self.combo_type.currentIndexChanged.connect(self.form_stack.setCurrentIndex)

        self.materials_data = {}  #Diccionario para guardar materiales {tag: objeto}
        self.next_tag = 1
        #conectamos los botones
        self.btn_add.clicked.connect(self.add_material)
        self.btn_delete.clicked.connect(self.delete_material)

    def add_material(self):
        material_type = self.combo_type.currentText()

        #1. Recolectar la información del formulario activo
        if material_type == "Concrete01":
            data = self.form_concrete.get_data()
            name = f"Mat_Concreto_{self.next_tag}"
            
            new_material = Concrete01(self.next_tag, name,**data)

        elif material_type == "Steel01":
            data = self.form_steel.get_data()
            name = f"Mat_Acero_{self.next_tag}"
            new_material = Steel01(self.next_tag,name,**data)
        else:
            return 

        # Guardar logica
        self.materials_data[self.next_tag] = new_material

        #Acutalizar la lista en la UI
        display_text = f"{self.next_tag}-{name}({material_type})"
        self.materials_list.addItem(display_text)

        #Peparar el siguiente
        self.next_tag += 1
        print(f"[DEBUG] Material creado {new_material.get_opensees_args()}")

    def delete_material(self):
        current_row = self.materials_list.currentRow()
    
        if current_row >=0:
            item = self.materials_list.takeItem(current_row)
            # TODO: Remove from self.materials_data logic
            # (Requires parsing the tag from the text string, slightly complex)
            # For now, just removing from UI is enough visually.

            del item