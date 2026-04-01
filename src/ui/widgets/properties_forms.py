from src.analysis.manager import ProjectManager
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import (QWidget, QFormLayout, QDoubleSpinBox, QSpinBox,
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

        # --- Masa nodal (opcional) ---
        self.chk_mass = QCheckBox("Masa nodal")
        form_layout.addRow(self.chk_mass)
        self.widget_mass = QWidget()
        mass_layout = QFormLayout(self.widget_mass)
        self.widget_mass.setVisible(False)
        self.spin_mx = UnitSpinBox(UnitType.MASS)
        self.spin_mx.setRange(0.0, 99999999.0)
        self.spin_mx.setDecimals(6)
        self.spin_my = UnitSpinBox(UnitType.MASS)
        self.spin_my.setRange(0.0, 99999999.0)
        self.spin_my.setDecimals(6)
        self.spin_mrz = UnitSpinBox(UnitType.MASS)
        self.spin_mrz.setRange(0.0, 99999999.0)
        self.spin_mrz.setDecimals(6)
        mass_layout.addRow("Masa X:", self.spin_mx)
        mass_layout.addRow("Masa Y:", self.spin_my)
        mass_layout.addRow("Masa Rot. Z:", self.spin_mrz)
        form_layout.addRow(self.widget_mass)
        self.chk_mass.toggled.connect(self.widget_mass.setVisible)

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

        # Mostrar masa si el nodo la tiene
        if node.mass is not None:
            self.chk_mass.setChecked(True)
            self.spin_mx.set_value_base(node.mass[0])
            self.spin_my.set_value_base(node.mass[1])
            self.spin_mrz.set_value_base(node.mass[2])
        else:
            self.chk_mass.setChecked(False)

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

        # Guardar masa
        if self.chk_mass.isChecked():
            self.current_node.mass = [
                self.spin_mx.get_value_base(),
                self.spin_my.get_value_base(),
                self.spin_mrz.get_value_base()
            ]
        else:
            self.current_node.mass = None

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
        # Nodos (Editable - SpinBox)
        self.spin_node_i = QSpinBox()
        self.spin_node_i.setRange(1, 999999)
        self.spin_node_i.valueChanged.connect(self._on_value_changed)

        self.spin_node_j = QSpinBox()
        self.spin_node_j.setRange(1, 999999)
        self.spin_node_j.valueChanged.connect(self._on_value_changed)

        #Section (Editable - ComboBox)
        self.combo_section = QComboBox()
        self.combo_section.currentIndexChanged.connect(self._on_value_changed)
        
        form.addRow("Tag:", self.lbl_tag)
        form.addRow("Nodo Inicial (I):", self.spin_node_i)
        form.addRow("Nodo Final (J):", self.spin_node_j)
        
        self.lbl_sec = QLabel("Sección:")
        form.addRow(self.lbl_sec, self.combo_section)
        
        # --- Bloque Gesto Hinge ---
        self.widget_hinge = QWidget()
        hinge_layout = QFormLayout(self.widget_hinge)
        
        self.cb_sec_i = QComboBox()
        self.cb_sec_i.currentIndexChanged.connect(self._on_value_changed)
        self.cb_sec_j = QComboBox()
        self.cb_sec_j.currentIndexChanged.connect(self._on_value_changed)
        self.spin_lp_i = UnitSpinBox(UnitType.LENGTH)
        self.spin_lp_i.setDecimals(4)
        self.spin_lp_i.setRange(0.0001, 999.0)
        self.spin_lp_i.valueChanged.connect(self._on_value_changed)
        self.spin_lp_j = UnitSpinBox(UnitType.LENGTH)
        self.spin_lp_j.setDecimals(4)
        self.spin_lp_j.setRange(0.0001, 999.0)
        self.spin_lp_j.valueChanged.connect(self._on_value_changed)
        
        hinge_layout.addRow("Sección I:", self.cb_sec_i)
        hinge_layout.addRow("Lp_i:", self.spin_lp_i)
        hinge_layout.addRow("Sección J:", self.cb_sec_j)
        hinge_layout.addRow("Lp_j:", self.spin_lp_j)
        
        form.addRow(self.widget_hinge)
        self.widget_hinge.setVisible(False)

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
        # Cargar id de los nodos conectados
        self.spin_node_i.setValue(int(element.node_i))
        self.spin_node_j.setValue(int(element.node_j))
        #cargar secciones disponibles
        self.combo_section.clear()
        self.cb_sec_i.clear()
        self.cb_sec_j.clear()
        
        manager = ProjectManager.instance()
        sections = manager.section
        for tag, sec in sections.items():
            text = f"{tag}: {sec.name}"
            self.combo_section.addItem(text, userData=tag)
            self.cb_sec_i.addItem(text, userData=tag)
            self.cb_sec_j.addItem(text, userData=tag)
        # Selecciona la sección actual mediante el polimorfismo
        from src.analysis.element import ForceBeamColumnHinge
        if isinstance(element, ForceBeamColumnHinge):
            self.lbl_sec.setText("Sección Central (e):")
            self.widget_hinge.setVisible(True)
            
            idx_e = self.combo_section.findData(element.section_e_tag)
            if idx_e >= 0: self.combo_section.setCurrentIndex(idx_e)
            
            idx_i = self.cb_sec_i.findData(element.section_i_tag)
            if idx_i >= 0: self.cb_sec_i.setCurrentIndex(idx_i)
            
            idx_j = self.cb_sec_j.findData(element.section_j_tag)
            if idx_j >= 0: self.cb_sec_j.setCurrentIndex(idx_j)
            
            self.spin_lp_i.set_value_base(element.lp_i)
            self.spin_lp_j.set_value_base(element.lp_j)
        else:
            self.lbl_sec.setText("Sección Transversal:")
            self.widget_hinge.setVisible(False)
            
            if hasattr(element, 'section_tag'):
                idx = self.combo_section.findData(element.section_tag)
                if idx >= 0: self.combo_section.setCurrentIndex(idx)
        self.blockSignals(False)
        self.btn_apply.setEnabled(False)


    def _on_value_changed(self):
        self.btn_apply.setEnabled(True)

    def apply_changes(self):
        from src.analysis.element import ForceBeamColumnHinge
        if not self.current_element: return
        
        # Guardar nueva topología si cambió algún nodo
        old_i, old_j = self.current_element.node_i, self.current_element.node_j
        new_i = self.spin_node_i.value()
        new_j = self.spin_node_j.value()
        
        topology_changed = False
        if old_i != new_i or old_j != new_j:
            self.current_element.node_i = new_i
            self.current_element.node_j = new_j
            topology_changed = True

        if isinstance(self.current_element, ForceBeamColumnHinge):
            self.current_element.section_e_tag = self.combo_section.currentData()
            self.current_element.section_i_tag = self.cb_sec_i.currentData()
            self.current_element.section_j_tag = self.cb_sec_j.currentData()
            self.current_element.lp_i = self.spin_lp_i.get_value_base()
            self.current_element.lp_j = self.spin_lp_j.get_value_base()
        else:
            idx = self.combo_section.currentIndex()
            if idx >= 0:
                self.current_element.section_tag = self.combo_section.itemData(idx)
        
        if topology_changed:
            ProjectManager.instance().mark_topology_dirty()
        self.dataChanged.emit()
        self.btn_apply.setEnabled(False)

    


        
