from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QDoubleSpinBox, QPushButton, QVBoxLayout, QCheckBox,QHBoxLayout
from PyQt6.QtCore import pyqtSignal

class NodeForms(QWidget):
    dataChanged = pyqtSignal()
    def __init__(self):
        super().__init__()

        # Layout Principal Vertical
        main_layout = QVBoxLayout(self)
        
        # Layout del Formulario
        form_layout = QFormLayout()
        
        # Inputs        
        self.lbl_tag = QLabel("-")
        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-10000, 10000) # Rango amplio
        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-10000, 10000)

        #CheckBox para las restricciones

        self.chk_fix_x = QCheckBox("X")
        self.chk_fix_y = QCheckBox("Y")
        self.chk_fix_rz = QCheckBox("Rz")

        # Layout horizontal para los checkboxes
        fix_layout = QHBoxLayout()
        fix_layout.addWidget(self.chk_fix_x)
        fix_layout.addWidget(self.chk_fix_y)
        fix_layout.addWidget(self.chk_fix_rz)

        #Añadir al formulario
        form_layout.addRow("Tag (ID):", self.lbl_tag)
        form_layout.addRow("Coord X:", self.spin_x)
        form_layout.addRow("Coord Y:", self.spin_y)
        form_layout.addRow("Restricciones:",fix_layout)

        main_layout.addLayout(form_layout)
        # Botón de guardar
        self.btn_apply = QPushButton("Aplicar Cambios")
        self.btn_apply.clicked.connect(self.apply_changes)
        self.btn_apply.setEnabled(False)

        main_layout.addWidget(self.btn_apply)
        main_layout.addStretch() 

        self.current_node = None
        
    def load_node(self,node):
        #Carga datos en el form
        self.current_node = node
        self.lbl_tag.setText(str(node.tag))
        self.spin_x.setValue(node.x)
        self.spin_y.setValue(node.y)
        fixity= node.fixity
        self.chk_fix_x.setChecked(bool(fixity[0]))
        self.chk_fix_y.setChecked(bool(fixity[1]))
        self.chk_fix_rz.setChecked(bool(fixity[2]))
        self.btn_apply.setEnabled(True)

    def apply_changes(self):
        #Guarda cambios en el objetivo y emite señal
        if self.current_node:
            self.current_node.x = self.spin_x.value()
            self.current_node.y = self.spin_y.value()

            new_fixity = [
                1 if self.chk_fix_x.isChecked() else 0,
                1 if self.chk_fix_y.isChecked() else 0,
                1 if self.chk_fix_rz.isChecked() else 0
        ]
            self.current_node.fixity = new_fixity
            self.dataChanged.emit()



        
