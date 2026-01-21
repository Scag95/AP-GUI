from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QPushButton, QWidget, QLabel,
                             QComboBox,QStackedWidget,QListWidgetItem)
from PyQt6.QtCore import Qt

from src.ui.widgets.material_forms import ConcreteForm, SteelForm
from src.analysis.materials import Concrete01, Steel01
from src.analysis.manager import ProjectManager

class MaterialDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Definir Materiales")
        self.resize(800,600)

        #Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.main_layout = QHBoxLayout(self)

        #Panel Izquierdo (Lista)
        self.left_panel_layout = QVBoxLayout()

        self.materials_list  = QListWidget()
        self.left_panel_layout.addWidget(self.materials_list)

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

        #conectamos los botones
        self.btn_add.clicked.connect(self.add_material)
        self.btn_delete.clicked.connect(self.delete_material)

        #cargar materiales existentes
        self.load_materials()

    def add_material(self):
        material_type = self.combo_type.currentText()

        #Llamamos del ProjectManager el tag del material.
        manager = ProjectManager.instance()
        next_tag = manager.get_next_material_tag()

        #1. Recolectar la información del formulario activo
        if material_type == "Concrete01":
            data = self.form_concrete.get_data()
            name = f"Mat_Concreto_{next_tag}"
            
            material = Concrete01(next_tag, name,**data)

        elif material_type == "Steel01":
            data = self.form_steel.get_data()
            name = f"Mat_Acero_{next_tag}"
            material = Steel01(next_tag,name,**data)
        else:
            return 

        # Guardar logica
        manager.add_material(material)
        #Acutalizar la lista en la UI
        display_text = f"{next_tag}-{name}({material_type})"

        #Guardamos el ID del material en una "mochila"
        item=QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, material.tag)
        self.materials_list.addItem(item)

        print(f"[DEBUG] Material creado {material.get_opensees_args()}")

    def delete_material(self):
        current_row = self.materials_list.currentRow()
        manager = ProjectManager.instance()
        if current_row >=0:
            item = self.materials_list.item(current_row)
            tag_to_delete = item.data(Qt.ItemDataRole.UserRole)

            if tag_to_delete is not None:
                manager.delete_material(tag_to_delete)
            self.materials_list.takeItem(current_row)
            del item

    def load_materials(self):
        self.materials_list.clear()

        manager = ProjectManager.instance()
        materials = manager.get_all_materials()

        for  material in materials:
            mat_type = material.__class__.__name__
            display_text = f"{material.tag}-{material.name}({mat_type})"
            #Guardamos el ID del material en una "mochila"
            item=QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, material.tag)
            self.materials_list.addItem(item)


