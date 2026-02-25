import pyqtgraph as pg
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QComboBox, QPushButton, QLabel, QDialogButtonBox, QSlider, QHBoxLayout, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
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
        main_layout = QHBoxLayout(self)

        # Panel izquierdo para curvas
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Curvas a visualizar:</b>"))
        
        # Lista con Checkboxes para seleccionar múltiples curvas
        self.list_curves = QListWidget()
        self.list_curves.setFixedWidth(250)
        self.list_curves.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.list_curves.itemChanged.connect(self.update_plot)
        left_layout.addWidget(self.list_curves)
        
        # Etiqueta de información del paso actual (Multi-linea, debajo de la lista)
        self.lbl_plot_info = QLabel("")
        self.lbl_plot_info.setWordWrap(True)
        self.lbl_plot_info.setStyleSheet("color: white; font-size: 11px; margin-top: 10px;")
        left_layout.addWidget(self.lbl_plot_info)

        main_layout.addLayout(left_layout)

        # Panel derecho para plot y slider
        right_layout = QVBoxLayout()

        # Añadir item Global
        item_global = QListWidgetItem("Global (Base Shear vs Roof Drift)")
        item_global.setFlags(item_global.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item_global.setData(Qt.ItemDataRole.UserRole, "global")
        item_global.setCheckState(Qt.CheckState.Checked)  # Global activado por defecto
        self.list_curves.addItem(item_global)
        
        # Añadir pisos disponibles (ordenados)
        sorted_floors = sorted(self.results["floors"].keys())
        
        # Mapa de alturas -> Nombres de Piso
        self.floor_map = {}
        
        for i, y in enumerate(sorted_floors):
             floor_num = i + 1
             name = f"Piso {floor_num}"
             self.floor_map[y] = name
             
             label = f"{name} (Y={y:.2f})"
             item_floor = QListWidgetItem(label)
             item_floor.setFlags(item_floor.flags() | Qt.ItemFlag.ItemIsUserCheckable)
             item_floor.setData(Qt.ItemDataRole.UserRole, y)
             item_floor.setCheckState(Qt.CheckState.Unchecked)
             self.list_curves.addItem(item_floor)

        # --- GRAFICO ---
        um = UnitManager.instance()
        self.plot_widget = pg.PlotWidget(title = "Curva de capacidad (Pushover)")
        u_force = um.get_current_unit(UnitType.FORCE)
        u_len = um.get_current_unit(UnitType.LENGTH)
        self.plot_widget.setLabel('bottom', f"Desplazamiento Techo [{u_len}]")
        self.plot_widget.setLabel('left', f"Cortante Basal Vb [{u_force}]")
                
        self.plot_widget.getAxis('bottom').enableAutoSIPrefix(False)
        self.plot_widget.getAxis('left').enableAutoSIPrefix(False)

        self.plot_widget.showGrid(x=True, y=True, alpha = 0.3)
        self.plot_widget.setBackground('w')

        self.plot_widget.showGrid(x=True, y=True, alpha = 0.3)
        self.plot_widget.setBackground('w')

        right_layout.addWidget(self.plot_widget)

        # --- SLIDER DE PASOS ---
        slider_layout = QHBoxLayout()
        self.lbl_step = QLabel("Paso: Todos")
        self.slider_step = QSlider(Qt.Orientation.Horizontal)
        self.slider_step.setMinimum(0)
        self.slider_step.valueChanged.connect(self._on_slider_changed)
        
        slider_layout.addWidget(self.lbl_step)
        slider_layout.addWidget(self.slider_step)
        
        right_layout.addLayout(slider_layout)
        main_layout.addLayout(right_layout)
        
        self.current_step_val = None
        
        # Pintar inicial
        self.update_plot()

    def _on_slider_changed(self, value):
        self.current_step_val = value
        self.update_plot()

    def update_plot(self):
        # Limpiar gráfico
        self.plot_widget.clear()

        # 1. Obtener claves seleccionadas
        selected_keys = []
        for i in range(self.list_curves.count()):
            item = self.list_curves.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_keys.append(item.data(Qt.ItemDataRole.UserRole))

        if not selected_keys: return

        um = UnitManager.instance()
        u_len = um.get_current_unit(UnitType.LENGTH)
        u_force = um.get_current_unit(UnitType.FORCE)

        # 3. Configurar Ejes y Título (Genérico al soportar múltiples)
        self.plot_widget.setTitle("Comparativa Curvas de Capacidad")
        self.plot_widget.setLabel('bottom', f"Desplazamiento / Deriva [{u_len}]")
        self.plot_widget.setLabel('left', f"Cortante [{u_force}]")

        # Acumuladores globales para fijar la escala
        max_limit_x = 0
        max_limit_y = 0

        # Para configurar el Slider necesitamos el máximo de pasos de alguna curva (suelen ser las mismas)
        global_max_steps = 0
        curves_data = []

        # 2. Obtener Datos Base para todas las curvas activas
        for data_key in selected_keys:
            dx, dy = [], []
            name = ""

            if data_key == "global":
                dx = self.results.get("roof_disp", [])
                dy = self.results.get("base_shear", [])
                name = "Global"
            elif data_key in self.results["floors"]:
                floor_data = self.results["floors"][data_key]
                dx = floor_data["disp"]
                dy = floor_data["shear"]
                name = self.floor_map.get(data_key, f"Y={data_key:.2f}")

            if not dx or not dy: continue
            
            global_max_steps = max(global_max_steps, len(dx))
            curves_data.append({"key": data_key, "name": name, "dx": dx, "dy": dy})

        if not curves_data: return

        # Configurar limites del Slider
        self.slider_step.blockSignals(True)
        if self.slider_step.maximum() != global_max_steps:
            self.slider_step.setMaximum(global_max_steps)
            if self.current_step_val is None or self.current_step_val > global_max_steps:
                self.slider_step.setValue(global_max_steps)
                self.current_step_val = global_max_steps
        self.slider_step.blockSignals(False)
        
        if self.current_step_val == global_max_steps:
            self.lbl_step.setText(f"Paso: Todos ({global_max_steps})")
        else:
            self.lbl_step.setText(f"Paso: {self.current_step_val} / {global_max_steps}")

        # Recortar datos según slider
        limit = self.current_step_val

        # Añadir leyenda genérica (ya que superponemos)
        self.plot_widget.addLegend()

        # Acumulador para el texto multi-línea
        info_lines = [f"<b>Paso: {limit}</b>"]

        # Dibujar cada curva
        for i, c_data in enumerate(curves_data):
            dx_full = c_data["dx"]
            dy_full = c_data["dy"]
            
            # Rebanar para animación
            dx_cut = dx_full[:limit]
            dy_cut = dy_full[:limit]

            # Convertir Unidades Puntos Reales
            vis_dx = [um.from_base(val, UnitType.LENGTH) for val in dx_cut]
            vis_dy = [um.from_base(val, UnitType.FORCE) for val in dy_cut]
            
            # Formatear la cadena de carga/desp para esta curva
            if vis_dx and vis_dy:
                # Usar color html basado en el índice para que coincida con el plot
                c_hex = pg.intColor(i, hues=len(curves_data), alpha=230).name()
                info_lines.append(f"<span style='color:{c_hex};'>&#9632;</span> <b>{c_data['name']}</b><br>Disp: {vis_dx[-1]:.4f} {u_len} | Cortante: {vis_dy[-1]:.2f} {u_force}")

            # Obtener el alcance teórico total (sin recorte) para anclar el auto-rango
            full_vis_dx = [um.from_base(val, UnitType.LENGTH) for val in dx_full]
            full_vis_dy = [um.from_base(val, UnitType.FORCE) for val in dy_full]
            if full_vis_dx: max_limit_x = max(max_limit_x, max([abs(x) for x in full_vis_dx]))
            if full_vis_dy: max_limit_y = max(max_limit_y, max([abs(y) for y in full_vis_dy]))

            # Color distinto para cada gráfica
            base_color = pg.intColor(i, hues=len(curves_data), alpha=230)
            
            # === DIBUJO CON SOPORTE PARA CICLOS (Opcional, usando un solo color consolidado por curva principal) ===
            cycle_ids = self.results.get("cycle_id", [])[:limit]
            has_cycles = (len(cycle_ids) == len(vis_dx))

            if has_cycles and c_data["key"] == "global":
                # Si queremos mantener el arcoiris de ciclos SOLO para el global y está solo él seleccionado
                if len(curves_data) == 1:
                    unique_cycles = sorted(list(set(cycle_ids)))
                    n_cycles = len(unique_cycles) if unique_cycles else 1
                    cycle_points = {c: {"x":[], "y":[]} for c in unique_cycles}
                    
                    for idx_p, c_id in enumerate(cycle_ids):
                        cycle_points[c_id]["x"].append(vis_dx[idx_p])
                        cycle_points[c_id]["y"].append(vis_dy[idx_p])
                    
                    for idx_c, c_id in enumerate(unique_cycles):
                        c_pts = cycle_points[c_id]
                        if not c_pts["x"]: continue
                        color = pg.intColor(idx_c, hues=n_cycles, values=1, maxValue=255, alpha=200)
                        self.plot_widget.plot(c_pts["x"], c_pts["y"], pen=pg.mkPen(color, width=3), name=f"Ciclo {c_id+1}" if idx_c == 0 else None)
                        
                    if vis_dx and vis_dy:
                        last_color = pg.intColor(cycle_ids[-1] if cycle_ids else (n_cycles-1), hues=n_cycles, values=1, maxValue=255, alpha=200)
                        self.plot_widget.plot([vis_dx[-1]], [vis_dy[-1]], pen=None, symbol='o', symbolBrush=last_color, symbolSize=8)
                    continue

            # MODO MULTICURVA NORMAL (Un color solido por curva)
            if vis_dx and vis_dy:
                self.plot_widget.plot(vis_dx, vis_dy, pen=pg.mkPen(base_color, width=3), name=c_data["name"])
                # Cursor rastreador final
                self.plot_widget.plot([vis_dx[-1]], [vis_dy[-1]], pen=None, symbol='o', symbolBrush=base_color, symbolSize=8)
                
        # Actualizar etiqueta texto multi-línea
        self.lbl_plot_info.setText("<br><br>".join(info_lines))

        # Trancar los límites para que no salte el zoom
        margin = 1.1
        if max_limit_x > 0: self.plot_widget.setXRange(0, max_limit_x * margin)
        if max_limit_y > 0: self.plot_widget.setYRange(0, max_limit_y * margin)