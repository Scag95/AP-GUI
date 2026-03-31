from src.ui.widgets.unit_spinbox import UnitSpinBox
from PyQt6.QtCore import qSetMessagePattern
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QComboBox, QDialogButtonBox, QLabel, 
                             QDoubleSpinBox, QCheckBox, QMessageBox)
from src.analysis.manager import ProjectManager
from src.analysis.loads import ElementLoad
from src.utils.units import UnitManager, UnitType

class SelfWeightDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Peso Propio")
        self.resize(800, 600)
        
        #Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.manager = ProjectManager.instance()

        layout = QVBoxLayout(self)

        #Formulaio
        form_layout = QFormLayout()

        #1. (Eliminado) Gravedad estática 9.81

        #2. Selector de Patrón
        self.combo_pattern = QComboBox()
        self.populate_patterns()
        form_layout.addRow("Patrón Destino:", self.combo_pattern)

        #3. Filtro vigas
        self.check_beams_only = QCheckBox("Aplicar solo a vigas (Horizontales)")
        self.check_beams_only.setChecked(False)
        form_layout.addRow("", self.check_beams_only)

        #4. Opcion de Reemplazo
        self.check_delete = QCheckBox("Eliminar cargas distribuidas existentes")
        self.check_delete.setToolTip("Si se marca, se borraran TODAS las cargas distruidas actiales en este Patrón antes de añadir el peso propio.")
        form_layout.addRow("",self.check_delete)

        layout.addLayout(form_layout)

        #Botones
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.generate_loads)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def populate_patterns(self):
        self.combo_pattern.clear()
        for p in self.manager.get_all_patterns():
            self.combo_pattern.addItem(f"[{p.tag}] {p.name}", p.tag)

    def generate_loads(self):
        if self.combo_pattern.count() == 0:
            QMessageBox.warning(self, "Aviso", "No hay Patrones de Carga. Crea uno en el Gestor de Patrones primero.")
            return

        g_val_visual = 9.81 # Fijo
        g_acc_base = UnitManager.instance().to_base(g_val_visual, UnitType.ACCELERATION)

        only_beams = self.check_beams_only.isChecked()
        delete_existing = self.check_delete.isChecked()
        # Lógica del cálculo
        try:
            count = self.apply_self_weight(g_acc_base, only_beams, delete_existing)
            QMessageBox.information(self, "Éxito", f"Se han generado {count} cargas de peso propio.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generando cargas: {str(e)}")

    def apply_self_weight(self, g, only_beams, delete_existing):
        pattern_tag = self.combo_pattern.currentData()
        pattern = self.manager.get_pattern(pattern_tag)
        if not pattern: return 0

        if delete_existing:
            loads_to_remove = [l.tag for l in pattern.loads if isinstance(l, ElementLoad)]
            for tag in loads_to_remove:
                self.manager.delete_load(tag)

        elements = self.manager.get_all_elements()
        new_loads_count = 0

        for ele in elements:
            # Geometría
            ni = self.manager.get_node(ele.node_i)
            nj = self.manager.get_node(ele.node_j)
            dx = nj.x - ni.x
            dy = nj.y - ni.y
            L = (dx**2 + dy**2)**0.5
            if L == 0: continue
            # Chequeo de "Es Viga Horizontal"
            is_beam = False
            if abs(dx) > 0:
                 if abs(dy) / abs(dx) < 0.1: # Pendiente < 10%
                     is_beam = True
            
            # Si el usuario quiere SOLO vigas y esto NO es una viga -> Saltar
            if only_beams and not is_beam:
                continue
            # Cálculo de Carga
            rho = ele.mass_density
            
            W = rho * g
                      
            wy = -W * (dx / L)
            wx = -W * (dy / L)
            
            load = ElementLoad(tag=0, element_tag=ele.tag, wy=wy, wx=wx)
            self.manager.add_load(load, pattern_tag)
            new_loads_count += 1
            
        return new_loads_count
