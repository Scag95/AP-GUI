from PyQt6.QtWidgets import (QWidget, QFormLayout, QGroupBox, QComboBox,
                             QSpinBox, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox)
from src.analysis.manager import ProjectManager
from src.analysis.materials import Concrete01, Steel01
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitType
import math


class SectionForm(QWidget):
    def __init__(self):
        super().__init__()
        #Panel Derecho
        layout = QFormLayout(self)
        
        #Nombre de la Sección
        self.textbox_name = QLineEdit()
        self.textbox_name.setPlaceholderText("ej: Viga_300x500")
        layout.addRow("Nombre de la sección",self.textbox_name)
        
        #Base
        self.spin_b = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_b.setRange(0, 1e6) # Rango amplio visual (ej. 1,000,000 mm)
        self.spin_b.setDecimals(2)   # 2 decimales fijos
        self.spin_b.set_value_base(0.3) # 300 mm = 0.3 m
        self.spin_b.setSingleStep(10)
        layout.addRow("Base de la sección:", self.spin_b)

        #Altura
        self.spin_h = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_h.setRange(0,1e6)  # Rango amplio visual (ej. 1,000,000 mm)
        self.spin_h.setDecimals(2)   # 2 decimales fijos
        self.spin_h.set_value_base(0.3)    # 300 mm = 0.3 m
        self.spin_h.setSingleStep(10)
        layout.addRow("Altura de la sección:",self.spin_h)

        self.combo_concrete = QComboBox()
        self.combo_steel = QComboBox()
        
        # Llenar los combos
        self.populate_materials()
        
        layout.addRow("Material Concreto:", self.combo_concrete)
        layout.addRow("Material Acero:", self.combo_steel)

        # --- Recubrimiento ---
        self.spin_cover = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_cover.setRange(0, 1e6)
        self.spin_cover.setDecimals(2)
        self.spin_cover.set_value_base(0.040)
        layout.addRow("Recubrimiento:", self.spin_cover)

        # --- Refuerzo Superior ---
        # Usamos un GroupBox para que se vea ordenado
        group_top = QGroupBox("Refuerzo Superior")
        form_top = QFormLayout() 
        group_top.setLayout(form_top)
        
        self.spin_top_qty = QSpinBox()
        self.spin_top_qty.setRange(0, 50)
        self.spin_top_qty.setValue(3)
        form_top.addRow("Cantidad:", self.spin_top_qty)
        
        self.spin_top_diam = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_top_diam.setRange(0, 100)
        self.spin_top_diam.setDecimals(2)
        self.spin_top_diam.set_value_base(0.020)
        form_top.addRow("Diámetro:", self.spin_top_diam)
        
        layout.addRow(group_top)
        # --- Refuerzo Inferior ---
        group_bot = QGroupBox("Refuerzo Inferior")
        form_bot = QFormLayout()
        group_bot.setLayout(form_bot)
        
        self.spin_bot_qty = QSpinBox()
        self.spin_bot_qty.setRange(0, 50)
        self.spin_bot_qty.setValue(3)
        form_bot.addRow("Cantidad:", self.spin_bot_qty)
        
        self.spin_bot_diam = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_bot_diam.setRange(0, 100)
        self.spin_bot_diam.setDecimals(2)
        self.spin_bot_diam.set_value_base(0.020)
        form_bot.addRow("Diámetro:", self.spin_bot_diam)
        
        layout.addRow(group_bot)


        # --- Refuerzo Izquierdo ---
        group_left = QGroupBox("Refuerzo Izquierdo")
        form_left = QFormLayout()
        group_left.setLayout(form_left)

        self.spin_left_qty = QSpinBox()
        self.spin_left_qty.setRange(0,50)
        self.spin_left_qty.setValue(0)
        form_left.addRow("Cantidad", self.spin_left_qty)

        self.spin_left_diam = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_left_diam.setRange(0, 100)
        self.spin_left_diam.setDecimals(2)
        self.spin_left_diam.set_value_base(0.020)
        form_left.addRow("Diámetro:", self.spin_left_diam)

        layout.addRow(group_left)

        # --- Refuerzo Derecho ---

        group_right = QGroupBox("Refuerzo Izquierdo")
        form_right = QFormLayout()
        group_right.setLayout(form_right)

        self.spin_right_qty = QSpinBox()
        self.spin_right_qty.setRange(0,50)
        self.spin_right_qty.setValue(0)
        form_right.addRow("Cantidad", self.spin_right_qty)

        self.spin_right_diam = UnitSpinBox(UnitType.SECTION_DIM)
        self.spin_right_diam.setRange(0, 100)
        self.spin_right_diam.setDecimals(2)
        self.spin_right_diam.set_value_base(0.020)
        form_right.addRow("Diámetro:", self.spin_right_diam)

        layout.addRow(group_right)

        # --- Discretización ---
        group_subdivision = QGroupBox("Discretización")
        form_subdivision = QFormLayout()
        group_subdivision.setLayout(form_subdivision)

        self.spin_nIy = QSpinBox()
        self.spin_nIy.setValue(10)
        form_subdivision.addRow("Número de subdivisión en Y", self.spin_nIy)

        self.spin_nIz = QSpinBox()
        self.spin_nIz.setValue(10)
        form_subdivision.addRow("Número de subdivisión en Z", self.spin_nIz)
        layout.addRow(group_subdivision)

    def populate_materials(self):
        self.combo_concrete.clear()
        self.combo_steel.clear()

        materials = ProjectManager.instance().get_all_materials()

        for mat in materials:
            display_text = f"{mat.tag} - {mat.name} ({mat.__class__.__name__})"

            if isinstance(mat, Concrete01):
                self.combo_concrete.addItem(display_text, mat.tag)

            elif isinstance(mat, Steel01):
                self.combo_steel.addItem(display_text, mat.tag)

    def get_data(self):
        #Devuelve los valores del formulario
        return{
            "name": self.textbox_name.text(),
            "b": self.spin_b.get_value_base(),
            "h": self.spin_h.get_value_base(),
            "concrete": self.combo_concrete.currentData(),
            "steel": self.combo_steel.currentData(),
            "cover": self.spin_cover.get_value_base(),
            "bot_qty": self.spin_bot_qty.value(),
            "bot_diam": self.spin_bot_diam.get_value_base(),
            "top_qty": self.spin_top_qty.value(),
            "top_diam": self.spin_top_diam.get_value_base(),
            "left_qty": self.spin_left_qty.value(),
            "left_diam": self.spin_left_diam.get_value_base(),
            "right_qty": self.spin_right_qty.value(),
            "right_diam": self.spin_right_diam.get_value_base(),
            "nIy": self.spin_nIy.value(),
            "nIz": self.spin_nIz.value()
        }

    def set_data(self, section):
        if not section: return

        #1. Nombre
        self.textbox_name.setText(section.name)
        
        #2. Geometría
        if section.patches and len(section.patches) > 0:
            core = section.patches[0]
            # h  = yJ - yI
            h = abs(core.yJ - core.yI)
            # b = zJ - zI
            b = abs(core.zJ - core.zI)

            self.spin_h.set_value_base(h)
            self.spin_b.set_value_base(b)

            idx = self.combo_concrete.findData(core.material_tag)
            if idx >= 0:
                self.combo_concrete.setCurrentIndex(idx)
                
        self.spin_top_qty.setValue(0)
        self.spin_bot_qty.setValue(0)
        self.spin_left_qty.setValue(0)
        self.spin_right_qty.setValue(0)

        found_steel_mat = False

        for layer in section.layers:
            if not found_steel_mat:
                idx = self.combo_steel.findData(layer.material_tag)
                if idx>=0:
                    self.combo_steel.setCurrentIndex(idx)
                    found_steel_mat = True

            diam = math.sqrt(4*layer.area_bar/math.pi)

            # Opción A: Por orientación geométrica
            # Verificamos si es una línea horizontal o vertical (con un pequeño margen de tolerancia por redondeo)
            tol = 1e-6

            if abs(layer.yStart - layer.yEnd) <= tol:
                # Línea Horizontal (Superior o Inferior)
                if layer.yStart > 0:
                    self.spin_top_qty.setValue(layer.num_bars)
                    self.spin_top_diam.set_value_base(diam)
                    h_val = self.spin_h.get_value_base()
                    cover = (h_val/2) - layer.yStart
                    if cover > 0:
                        self.spin_cover.set_value_base(cover)
                elif layer.yStart < 0:
                    self.spin_bot_qty.setValue(layer.num_bars)
                    self.spin_bot_diam.set_value_base(diam)

            elif abs(layer.zStart - layer.zEnd) <= tol:
                # Línea Vertical (Izquierda o Derecha)
                if layer.zStart < 0:
                    self.spin_left_qty.setValue(layer.num_bars)
                    self.spin_left_diam.set_value_base(diam)
                elif layer.zStart > 0:
                    self.spin_right_qty.setValue(layer.num_bars)
                    self.spin_right_diam.set_value_base(diam)


class AggregatorForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # 1. Nombre
        form_layout = QFormLayout()
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("ej: Columna_Articulada_Vy")
        form_layout.addRow("Nombre:", self.txt_name)

        # 2. Sección Base (FiberSection)
        self.combo_base_sec = QComboBox()
        form_layout.addRow("Sección Base (Opcional):", self.combo_base_sec)
        
        layout.addLayout(form_layout)

        # 3. Aggregations (Materials & DOFs)
        group_agg = QGroupBox("Materiales a Agregar")
        agg_layout = QVBoxLayout()
        group_agg.setLayout(agg_layout)

        # Combo de Material y DOF
        h_layout = QHBoxLayout()
        self.combo_mat = QComboBox()
        self.combo_dof = QComboBox()
        self.combo_dof.addItems(["Vy", "P", "Mz"])

        self.btn_add_mat = QPushButton("Añadir al DOF")
        self.btn_add_mat.clicked.connect(self.add_aggregation)

        h_layout.addWidget(QLabel("Material:"))
        h_layout.addWidget(self.combo_mat, stretch=2)
        h_layout.addWidget(QLabel("DOF:"))
        h_layout.addWidget(self.combo_dof, stretch=1)
        h_layout.addWidget(self.btn_add_mat)
        
        agg_layout.addLayout(h_layout)

        # Lista visual de agregaciones
        self.list_agg = QListWidget()
        
        # Botón para borrar el seleccionado de la lista
        self.btn_del_mat = QPushButton("Borrar Seleccionado")
        self.btn_del_mat.clicked.connect(self.del_aggregation)

        agg_layout.addWidget(self.list_agg)
        agg_layout.addWidget(self.btn_del_mat)

        layout.addWidget(group_agg)

        # Cache de los mats agregados para luego extraerlos con get_data
        self.aggregations = [] # list of dicts: {"mat_tag": int, "dof": str, "mat_text": str}

    def populate(self, manager):
        # Poblar Base Sections
        self.combo_base_sec.clear()
        self.combo_base_sec.addItem("Ninguna", None)
        for sec in manager.get_all_sections():
            from src.analysis.sections import FiberSection
            if isinstance(sec, FiberSection):
                self.combo_base_sec.addItem(f"[{sec.tag}] {sec.name}", sec.tag)

        # Poblar Materiales
        self.combo_mat.clear()
        for mat in manager.get_all_materials():
            self.combo_mat.addItem(f"[{mat.tag}] {mat.name} ({mat.__class__.__name__})", mat.tag)

    def add_aggregation(self):
        mat_tag = self.combo_mat.currentData()
        mat_text = self.combo_mat.currentText()
        dof = self.combo_dof.currentText()

        if mat_tag is None:
            return

        # Simple validacion de que no se agregó el mismo DOF
        for a in self.aggregations:
            if a["dof"] == dof:
                QMessageBox.warning(self, "Aviso", f"El grado de libertad {dof} ya tiene un material asignado.")
                return

        self.aggregations.append({"mat_tag": mat_tag, "dof": dof, "mat_text": mat_text})
        self.refresh_list()

    def del_aggregation(self):
        row = self.list_agg.currentRow()
        if row >= 0:
            del self.aggregations[row]
            self.refresh_list()

    def refresh_list(self):
        self.list_agg.clear()
        for agg in self.aggregations:
            self.list_agg.addItem(f"DOF: {agg['dof']} <-- Mat: {agg['mat_text']}")

    def get_data(self):
        base_sec = self.combo_base_sec.currentData()
        return {
            "name": self.txt_name.text(),
            "base_section_tag": base_sec,
            "materials": [{"mat_tag": a["mat_tag"], "dof": a["dof"]} for a in self.aggregations]
        }

    def set_data(self, section, manager):
        self.txt_name.setText(section.name)
        
        # Seleccionar base section
        if section.base_section_tag is None:
            self.combo_base_sec.setCurrentIndex(0)
        else:
            idx = self.combo_base_sec.findData(section.base_section_tag)
            if idx >= 0:
                self.combo_base_sec.setCurrentIndex(idx)

        # Reconstruir lista de agregaciones
        self.aggregations = []
        for m in section.materials:
            mat_tag = m["mat_tag"]
            dof = m["dof"]
            # Buscar texto del material
            mat_text = f"Material {mat_tag}"
            mat = manager.get_material(mat_tag)
            if mat:
                 mat_text = f"[{mat.tag}] {mat.name} ({mat.__class__.__name__})"
            
            self.aggregations.append({"mat_tag": mat_tag, "dof": dof, "mat_text": mat_text})
        
        self.refresh_list()