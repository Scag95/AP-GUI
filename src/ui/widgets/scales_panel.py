from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QLabel, QGroupBox
from PyQt6.QtCore import Qt
from src.utils.scale_manager import ScaleManager

class ScalesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Control de Escalas")
        self.scale_manager = ScaleManager.instance()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)
        
        # Helper list to block signals during update
        self.spinboxes = {}

        # 1. Group: Visualización General
        group_general = QGroupBox("Visualización General")
        form_general = QFormLayout(group_general)
        
        self.spin_node = self._create_spinbox('node_size', 0.1, 10.0, 0.25, 2)
        form_general.addRow("Tamaño de Nodos (x):", self.spin_node)
        
        self.spin_load = self._create_spinbox('load', 0.1, 100.0, 0.25, 2)
        form_general.addRow("Escala de Cargas (x):", self.spin_load)
        
        self.spin_deform = self._create_spinbox('deformation', 0.1, 100.0, 0.25, 2)
        form_general.addRow("Deformada (x):", self.spin_deform)
        
        self.layout.addWidget(group_general)

        # 2. Group: Diagramas de Fuerzas
        group_diagrams = QGroupBox("Diagramas de Fuerzas")
        form_diagrams = QFormLayout(group_diagrams)
        
        self.spin_moment = self._create_spinbox('moment', 0.1, 100.0, 0.25, 2)
        form_diagrams.addRow("Momento M (x):", self.spin_moment)
        
        self.spin_shear = self._create_spinbox('shear', 0.1, 100.0, 0.25, 2)
        form_diagrams.addRow("Cortante V (x):", self.spin_shear)
        
        self.spin_axial = self._create_spinbox('axial', 0.1, 100.0, 0.25, 2)
        form_diagrams.addRow("Axial P (x):", self.spin_axial)
        
        self.layout.addWidget(group_diagrams)
        
        self.layout.addStretch()

        # Update fields initially and connect to external multiplier changes
        self._update_all_spinboxes()
        self.scale_manager.multiplier_changed.connect(self._on_external_multiplier_changed)

    def _create_spinbox(self, scale_key, min_val, max_val, step, decimals):
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setSingleStep(step)
        spin.setDecimals(decimals)
        
        # Evento manual del usuario
        spin.valueChanged.connect(lambda val, key=scale_key: self._on_spinbox_changed(key, val))
        
        self.spinboxes[scale_key] = spin
        return spin

    def _update_all_spinboxes(self):
        for key, spin in self.spinboxes.items():
            spin.blockSignals(True)
            spin.setValue(self.scale_manager.get_user_multiplier(key))
            spin.blockSignals(False)

    def _on_external_multiplier_changed(self, scale_type, multiplier):
        """Si el factor cambia programáticamente, actualizar UI pero sin emitir"""
        if scale_type in self.spinboxes:
            spin = self.spinboxes[scale_type]
            spin.blockSignals(True)
            spin.setValue(multiplier)
            spin.blockSignals(False)

    def _on_spinbox_changed(self, scale_type, value):
        """Si el usuario escribe/pincha en el spinbox, inyectar cambio al manager como multiplicador"""
        self.scale_manager.set_user_multiplier(scale_type, value)
