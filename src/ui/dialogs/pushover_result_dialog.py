import pyqtgraph as pg
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QComboBox, QPushButton, QLabel, QDialogButtonBox)
from src.analysis.manager import ProjectManager
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitManager
from src.utils.units import UnitType


class PushoverResultsDialog(QDialog):
    def __init__(self, results, parent = None):
        super().__init__(parent)
        self.results = results
        self.setWindowTitle("Análisis Pushover")
        self.resize(800, 600)
        
        #Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.manager = ProjectManager.instance()

        #Layout Principal
        layout = QVBoxLayout(self)

        # Combo para seleccionar curva
        form_layout = QFormLayout()
        self.combo_curve = QComboBox()
        self.combo_curve.addItem("Global (Base Shear vs Roof Drift)", userData="global")
        
        # Añadir pisos disponibles (ordenados)
        sorted_floors = sorted(self.results["floors"].keys())
        for y in sorted_floors:
             self.combo_curve.addItem(f"Piso Y={y:.2f} (Story Shear vs Drift)", userData=y)
             
        self.combo_curve.currentIndexChanged.connect(self.update_plot)
        form_layout.addRow("Curva a visualizar:", self.combo_curve)
        layout.addLayout(form_layout)

        # --- GRAFICO ---
        um = UnitManager.instance()
        self.plot_widget = pg.PlotWidget(title = "Curva de capacidad (Pushover)")
        u_force = um.get_current_unit(UnitType.FORCE)
        u_len = um.get_current_unit(UnitType.LENGTH)
        self.plot_widget.setLabel('bottom', f"Desplazamiento Techo [{u_len}]")
        self.plot_widget.setLabel('left', f"Cortante Basal Vb [{u_force}]")
                
        self.plot_widget.getAxis('bottom').enableAutoSIPrefix(False)
        self.plot_widget.getAxis('left').enableAutoSIPrefix(False)

        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('w')

        self.curve_item = self.plot_widget.plot([],[],pen = pg.mkPen('b',width = 3))
        layout.addWidget(self.plot_widget)
        
        # Pintar inicial
        self.update_plot()

    def update_plot(self):
        data_key = self.combo_curve.currentData()
        um = UnitManager.instance()
        u_len = um.get_current_unit(UnitType.LENGTH)
        u_force = um.get_current_unit(UnitType.FORCE)

        # 1. Determinar Datos y Etiquetas
        if data_key == "global":
            dx = self.results["roof_disp"]
            dy = self.results["base_shear"]
            title = "Global Pushover (Base Shear vs Roof Drift)"
            xlabel = f"Desplazamiento Techo [{u_len}]"
            ylabel = f"Cortante Basal [{u_force}]"
        else:
            # Es un piso específico (data_key es la altura 'y')
            y = data_key
            floor_data = self.results["floors"][y]
            dx = floor_data["disp"]
            dy = floor_data["shear"]
            title = f"Story Capacity Curve (Y={y:.2f})"
            xlabel = f"Desplazamiento Piso [{u_len}]"
            ylabel = f"Cortante de Piso [{u_force}]"

        # 2. Actualizar UI Plot
        self.plot_widget.setTitle(title)
        self.plot_widget.setLabel('bottom', xlabel)
        self.plot_widget.setLabel('left', ylabel)

        # 3. Convertir Unidades
        vis_dx = [um.from_base(val, UnitType.LENGTH) for val in dx]
        vis_dy = [um.from_base(val, UnitType.FORCE) for val in dy]
        
        self.curve_item.setData(vis_dx, vis_dy)