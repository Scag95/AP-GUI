from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QComboBox,
                              QPushButton, QDialogButtonBox,QLabel)
from src.analysis.manager import ProjectManager
from src.analysis.frame_generator import FrameGenerator

class gridDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grilla")
        self.resize(400,600)

        self.manager = ProjectManager.instance()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # -- Geometría --
        self.stories_input = QSpinBox()
        self.stories_input.setValue(1)
        self.stories_input.setMinimum(1)

        self.bays_input = QSpinBox()
        self.bays_input.setValue(1)
        self.bays_input.setMinimum(1)

        self.story_height_input = QDoubleSpinBox()
        self.story_height_input.setValue(3.0) # Metros
        self.story_height_input.setSuffix(" m")
        self.story_height_input.setMinimum(0.1)

        self.bay_width_input = QDoubleSpinBox()
        self.bay_width_input.setValue(3.0) # Metros
        self.bay_width_input.setSuffix(" m")
        self.bay_width_input.setMinimum(0.1)

        form_layout.addRow("Numero de Pisos:",self.stories_input)
        form_layout.addRow("Número de Vanos:", self.bays_input)
        form_layout.addRow("Altura de Entrepisos",self.story_height_input)
        form_layout.addRow("Ancho de vano",self.bay_width_input)

        #--- Secciones ---
        # Neceitamos elegir que seeción usar para vigas y columnas
        self.col_sec_combo = QComboBox()
        self.beam_sec_combo = QComboBox()

        self.populate_sections()

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
            "story_height": self.story_height_input.value(),
            "bay_width": self.bay_width_input.value(),
            # currentData() devuelve el TAG que guardamos (el segundo argumento en addItem)
            "col_sec_tag": self.col_sec_combo.currentData(),
            "beam_sec_tag": self.beam_sec_combo.currentData()
        }


        