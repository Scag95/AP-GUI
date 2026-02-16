from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QSpinBox, QComboBox, QPushButton,
                             QDialogButtonBox,QCheckBox)
from src.analysis.manager import ProjectManager
from src.analysis.frame_generator import FrameGenerator
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitType

class gridDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grilla")
        self.resize(400,600)

        self.manager = ProjectManager.instance()

        self.init_ui()

        #Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # -- Geometría --
        self.stories_input = QSpinBox()
        self.stories_input.setValue(1)
        self.stories_input.setMinimum(0)

        self.bays_input = QSpinBox()
        self.bays_input.setValue(1)
        self.bays_input.setMinimum(0)

        self.story_height_input = UnitSpinBox(UnitType.LENGTH)
        self.story_height_input.set_value_base(3.0) 
        self.story_height_input.setMinimum(0.1)

        self.bay_width_input = UnitSpinBox(UnitType.LENGTH)
        self.bay_width_input.set_value_base(3.0)
        self.bay_width_input.setMinimum(0.1)

        self.check_base_beams = QCheckBox("Generar vigas en la base (z=0)")
        self.check_base_beams.setChecked(False) # Por defecto NO

        # -- Añadir puntos de integración en el elemento" --
        self.integration_points = QSpinBox()
        self.integration_points.setValue(5)
        self.integration_points.setMaximum(10)
        self.integration_points.setMinimum(3)      

        form_layout.addRow("Numero de Pisos:",self.stories_input)
        form_layout.addRow("Número de Vanos:", self.bays_input)
        form_layout.addRow("Altura de Entrepisos",self.story_height_input)
        form_layout.addRow("Ancho de vano",self.bay_width_input)
        form_layout.addRow(self.check_base_beams)

        #--- Secciones ---
        # Neceitamos elegir que seeción usar para vigas y columnas
        self.col_sec_combo = QComboBox()
        self.beam_sec_combo = QComboBox()

        self.populate_sections()
        
        form_layout.addRow("Puntos de integración", self.integration_points)
        form_layout.addRow("Seccion Columnas:",self.col_sec_combo)
        form_layout.addRow("Sección Vigas:", self.beam_sec_combo)

        layout.addLayout(form_layout)

        # --- Botones ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


    def populate_sections(self):
        sections = self.manager.get_all_sections()
        for sec in sections:
            #El item guarda el nombre visible y el TAG como data oculta
            item_text= f"{sec.name} - Id {sec.tag}"
            self.col_sec_combo.addItem(item_text, sec.tag)
            self.beam_sec_combo.addItem(item_text, sec.tag)

    def get_data(self):
        return{
            "stories": self.stories_input.value(),
            "bays": self.bays_input.value(),
            "story_height": self.story_height_input.get_value_base(),
            "bay_width": self.bay_width_input.get_value_base(),
            # currentData() devuelve el TAG que guardamos (el segundo argumento en addItem)
            "col_sec_tag": self.col_sec_combo.currentData(),
            "beam_sec_tag": self.beam_sec_combo.currentData(),
            "add_base_beams": self.check_base_beams.isChecked(), 
            "integration_points":self.integration_points.value()
        }


        