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

        #1. Valor de gravedad
        self.spin_g = UnitSpinBox(UnitType.ACCELERATION)
        self.spin_g.setRange(0,1e5)
        self.spin_g.set_value_base(9.81)
        self.spin_g.setDecimals(2)
        form_layout.addRow("Aceleración Gravedad (g):", self.spin_g)

        #2. Filtro vigas
        self.check_beams_only = QCheckBox("Aplicar solo a vigas (Horizontales)")
        self.check_beams_only.setChecked(False)
        form_layout.addRow("", self.check_beams_only)

        #3. Opcion de Reemplazo
        self.check_delete = QCheckBox("Eliminar cargas distribuidas existentes")
        self.check_delete.setToolTip("Si se marca, se borraran TODAS las cargas distruidas actiales antes de añadir el peso propio.")
        form_layout.addRow("",self.check_delete)

        layout.addLayout(form_layout)

        #Botones
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.generate_loads)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def generate_loads(self):
        g_val_visual = self.spin_g.value()
        g_acc_base = UnitManager.instance().to_base(g_val_visual, UnitType.ACCELERATION)
        delete_existing = self.check_delete.isChecked()

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
        if delete_existing:
            loads_to_remove = [l.tag for l in self.manager.get_all_loads() if isinstance(l, ElementLoad)]
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
            self.manager.add_load(load)
            new_loads_count += 1
            
        return new_loads_count
