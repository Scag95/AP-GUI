from src.analysis.manager import ProjectManager
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import (QWidget, QFormLayout, QDoubleSpinBox, 
                             QLineEdit, QLabel, QVBoxLayout,QCheckBox,QHBoxLayout,QPushButton)
from PyQt6.QtCore import pyqtSignal
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitType

class NodeForms(QWidget):
    dataChanged = pyqtSignal()
    def __init__(self, parent = None):
        super().__init__(parent)

        # Layout Principal Vertical
        main_layout = QVBoxLayout(self)
        
        # Layout del Formulario
        form_layout = QFormLayout()
        
        # Inputs        
        self.lbl_tag = QLabel("-")
        self.spin_x = UnitSpinBox(UnitType.LENGTH)
        self.spin_x.setRange(-1e6, 1e6) # Rango amplio
        self.spin_x.setDecimals(3)

        self.spin_y = UnitSpinBox(UnitType.LENGTH)
        self.spin_y.setRange(-1e6, 1e6)
        self.spin_y.setDecimals(3)

        #Conectamos signals
        self.spin_x.valueChanged.connect(self._on_value_changed)
        self.spin_y.valueChanged.connect(self._on_value_changed)


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
        # Carga datos en el form
        self.current_node = node
        self.lbl_tag.setText(str(node.tag))
        # Bloqueamos la señal
        self.spin_x.blockSignals(True)
        self.spin_y.blockSignals(True)
        # Definimos los valores base
        self.spin_x.set_value_base(node.x)
        self.spin_y.set_value_base(node.y)
        # Desbloqueammos la señal
        self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(False)

        fixity= node.fixity
        self.chk_fix_x.setChecked(bool(fixity[0]))
        self.chk_fix_y.setChecked(bool(fixity[1]))
        self.chk_fix_rz.setChecked(bool(fixity[2]))
        self.btn_apply.setEnabled(True)

    def apply_changes(self):
        #Guarda cambios en el objetivo y emite señal
        if self.current_node:
            self.current_node.x = self.spin_x.get_value_base()
            self.current_node.y = self.spin_y.get_value_base()

            new_fixity = [
                1 if self.chk_fix_x.isChecked() else 0,
                1 if self.chk_fix_y.isChecked() else 0,
                1 if self.chk_fix_rz.isChecked() else 0
        ]
            self.current_node.fixity = new_fixity
            self.dataChanged.emit()

    def _on_value_changed(self):
        """Habilita el botón de aplicar cuando hay cambios pendientes."""
        if self.current_node:
            self.btn_apply.setEnabled(True)

class ElementForm(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self,parent = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        #Campos
        self.lbl_tag = QLabel("-")
        self.lbl_conn = QLabel("-")

        #Mass Density (Editable)
        self.spin_rho = UnitSpinBox(UnitType.DENSITY)
        self.spin_rho.setRange(0,1e9)
        self.spin_rho.setDecimals(2)
        self.spin_rho.valueChanged.connect(self._on_value_changed)

        #Section (Editable - ComboBox)
        self.combo_section = QComboBox()
        self.combo_section.currentIndexChanged.connect(self._on_value_changed)
        form.addRow("Tag:", self.lbl_tag)
        form.addRow("Nodos:", self.lbl_conn)
        form.addRow("Desnidad:", self.spin_rho)
        form.addRow("Sección:",self.combo_section)

        self.layout.addLayout(form)
        
        #Boton Aplicar
        self.btn_apply = QPushButton("Aplicar Cambios")
        self.btn_apply.clicked.connect(self.apply_changes)
        self.btn_apply.setEnabled(False)
        self.layout.addWidget(self.btn_apply)
        self.layout.addStretch()

        self.current_element = None

    def load_element(self, element):
        self.current_element = element
        self.blockSignals(True)

        #Propiedades Básicas
        self.lbl_tag.setText(str(element.tag))
        self.lbl_conn.setText(f"{element.node_i} -> {element.node_j}")

        #Cargar densidad (si el atributo existe, si no 0)
        rho = getattr(element, 'mass_density',0.0)
        self.spin_rho.set_value_base(rho)

        #cargar secciones disponibles
        self.combo_section.clear()
        manager = ProjectManager.instance()
        sections = manager.section

        for tag, sec in sections.items():
            self.combo_section.addItem(f"{tag}: {sec.name}", userData = tag)

        #Seleciona la sección actial
        if hasattr(element, 'section_tag'):
            idx = self.combo_section.findData(element.section_tag)
            if idx>=0: self.combo_section.setCurrentIndex(idx)

        self.blockSignals(False)
        self.btn_apply.setEnabled(False)


    def _on_value_changed(self):
        self.btn_apply.setEnabled(True)

    def apply_changes(self):
        if not self.current_element: return
        
        #Guardar densidad
        self.current_element.mass_density = self.spin_rho.get_value_base()

        #Guardar sección
        idx = self.combo_section.currentIndex()
        if idx >= 0:
            sec_tag = self.combo_section.itemData(idx)
            self.current_element.section_tag = sec_tag

        self.dataChanged.emit()
        self.btn_apply.setEnabled(False)

    


        
