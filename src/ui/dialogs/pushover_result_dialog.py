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

        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('w')

        # No creamos self.curve_item fijo, lo haremos dinámico
        layout.addWidget(self.plot_widget)
        
        # Pintar inicial
        self.update_plot()

    def update_plot(self):
        # Limpiar gráfico
        self.plot_widget.clear()

        # 1. Obtener clave de datos
        idx = self.combo_curve.currentIndex()
        if idx < 0: return

        data_key = self.combo_curve.itemData(idx)
        um = UnitManager.instance()
        u_len = um.get_current_unit(UnitType.LENGTH)
        u_force = um.get_current_unit(UnitType.FORCE)

        # 2. Obtener Datos Base
        dx, dy = [], []
        title, xlabel, ylabel = "", "", ""

        if data_key == "global":
            dx = self.results.get("roof_disp", [])
            dy = self.results.get("base_shear", [])
            title = "Global Pushover (Base Shear vs Roof Drift)"
            xlabel = f"Desplazamiento Techo [{u_len}]"
            ylabel = f"Cortante Basal [{u_force}]"
        else:
            # Es un piso específico (data_key es la altura 'y')
            if data_key in self.results["floors"]:
                floor_data = self.results["floors"][data_key]
                dx = floor_data["disp"]
                dy = floor_data["shear"]
                title = f"Story Capacity Curve (Y={data_key:.2f})"
                xlabel = f"Desplazamiento Piso [{u_len}]"
                ylabel = f"Cortante de Piso [{u_force}]"
        
        if not dx or not dy: return

        # 3. Configurar Ejes y Título
        self.plot_widget.setTitle(title)
        self.plot_widget.setLabel('bottom', xlabel)
        self.plot_widget.setLabel('left', ylabel)

        # 4. Convertir Unidades
        vis_dx = [um.from_base(val, UnitType.LENGTH) for val in dx]
        vis_dy = [um.from_base(val, UnitType.FORCE) for val in dy]

        # 5. Lógica de Colores por Ciclo
        cycle_ids = self.results.get("cycle_id", [])
        
        # Verificar coincidencia de longitud
        has_cycles = (len(cycle_ids) == len(vis_dx))

        if has_cycles:
            # Agrupar puntos por ciclo
            unique_cycles = sorted(list(set(cycle_ids)))
            n_cycles = len(unique_cycles) if unique_cycles else 1
            
            # Map cycle -> list of points
            cycle_points = {c: {"x":[], "y":[]} for c in unique_cycles}
            
            for i, c_id in enumerate(cycle_ids):
                cycle_points[c_id]["x"].append(vis_dx[i])
                cycle_points[c_id]["y"].append(vis_dy[i])
            
            # Plotear cada grupo con color distinto
            for i, c_id in enumerate(unique_cycles):
                c_data = cycle_points[c_id]
                if not c_data["x"]: continue
                
                # Color distintivo (Hue varía de 0 a 1)
                color = pg.intColor(i, hues=n_cycles, values=1, maxValue=255, alpha=200)
                pen = pg.mkPen(color, width=3)
                
                # Añadir nombre a leyenda si queremos (opcional)
                self.plot_widget.plot(c_data["x"], c_data["y"], pen=pen, name=f"Ciclo {c_id+1}")
                
            # Añadir Leyenda si hay ciclos
            if n_cycles > 1:
                self.plot_widget.addLegend()

        else:
            # Modo Clásico (Azul)
            self.plot_widget.plot(vis_dx, vis_dy, pen=pg.mkPen('b', width=3))