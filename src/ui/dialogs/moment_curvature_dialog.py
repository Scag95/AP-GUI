from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QFrame)
import pyqtgraph as pg
import os
import glob
from src.analysis.manager import ProjectManager
from src.utils.units import UnitManager, UnitType 

class MomentCurvatureDialog(QDialog):
    def __init__(self, element_tag=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resultados de Sección: Momento-Curvatura")
        self.resize(1000, 700)
        self.manager = ProjectManager.instance()
        self.data_dir = "pushover_data"
        
        # Setup Plot Style
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        
        self.init_ui()
        self.load_available_elements()
        
        # Si nos pasaron un tag inicial, intentamos seleccionarlo
        if element_tag is not None:
            index = self.element_combo.findData(element_tag)
            if index >= 0:
                self.element_combo.setCurrentIndex(index)

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # --- Left Panel: Controls ---
        controls_frame = QFrame()
        controls_frame.setFixedWidth(250)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Element Selector
        controls_layout.addWidget(QLabel("Seleccionar Elemento:"))
        self.element_combo = QComboBox()
        self.element_combo.currentIndexChanged.connect(self._on_element_changed)
        controls_layout.addWidget(self.element_combo)
        
        # Section (Integration Point) Selector
        controls_layout.addWidget(QLabel("Punto de Integración:"))
        self.section_combo = QComboBox()
        self.section_combo.currentIndexChanged.connect(self.update_plot)
        controls_layout.addWidget(self.section_combo)

        # Variable Selector (Y Axis)
        controls_layout.addWidget(QLabel("Variable Eje Y:"))
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.addItems(["Momento (Mz)", "Fuerza Axial (P)", "Cortante (Vy)"])
        self.y_axis_combo.currentIndexChanged.connect(self.update_plot)
        controls_layout.addWidget(self.y_axis_combo)

        # Info Box
        self.info_label = QLabel("Seleccione un elemento para ver sus resultados.")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: gray; font-size: 11px;")
        controls_layout.addWidget(self.info_label)

        controls_layout.addStretch()
        main_layout.addWidget(controls_frame)

        # --- Right Panel: Plot ---
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', "Curvatura (rad/m)", units='1/m')
        self.plot_widget.setLabel('left', "Momento (Nm)", units='N*m')
        self.plot_widget.showGrid(x=True, y=True)
        
        # Legend
        self.legend = self.plot_widget.addLegend()

        main_layout.addWidget(self.plot_widget, 1)

    def load_available_elements(self):
        """Busca archivos de resultados en la carpeta data y filtra los validos."""
        if not os.path.exists(self.data_dir):
            self.info_label.setText(f"No se encontró la carpeta '{self.data_dir}'. Ejecute el análisis Pushover primero.")
            return

        # Find files matching ele_*_force.out
        files = glob.glob(os.path.join(self.data_dir, "ele_*_force.out"))
        
        manager = ProjectManager.instance()
        elements_found = []
        for f in files:
            # Extract ID: ele_12_force.out -> 12
            filename = os.path.basename(f)
            try:
                tag = int(filename.split('_')[1])
                # FILTRO: Solo mostrar si existe en el proyecto actual
                if manager.get_element(tag) is not None:
                    elements_found.append(tag)
            except:
                continue
        
        elements_found.sort()
        
        self.element_combo.blockSignals(True)
        self.element_combo.clear()
        if not elements_found:
             self.element_combo.addItem("Sin resultados")
             self.element_combo.setEnabled(False)
        else:
            for tag in elements_found:
                self.element_combo.addItem(f"Elemento {tag}", tag)
            self.element_combo.setEnabled(True)
        
        self.element_combo.blockSignals(False)

        # Trigger initial load if items exist
        if self.element_combo.count() > 0:
            self._on_element_changed()

    def _on_element_changed(self):
        ele_tag = self.element_combo.currentData()
        if ele_tag is None: return
        
        ele_tag = self.element_combo.currentData()
        if ele_tag is None: return
        
        manager = ProjectManager.instance()
        element = manager.get_element(ele_tag)

        if element is None:
            self.info_label.setText(f"Error: Elemento {ele_tag} no encontrado en proyecto.")
            self.section_combo.clear()
            self.plot_widget.clear()
            return

        # Cargar datos desde disco
        self.load_element_data(ele_tag)
        
        # Configurar puntos de integración
        num_points = getattr(element, 'integration_points', 5)

        self.section_combo.blockSignals(True)
        self.section_combo.clear()

        for i in range(1, num_points + 1):
            self.section_combo.addItem(f"Sección {i} (Lobatto)", i)

        self.section_combo.blockSignals(False)

        if self.section_combo.count() > 0:
            self.section_combo.setCurrentIndex(0)
            self.update_plot()


    def load_element_data(self, tag):
        """Lee los archivos .out y parsea los datos."""
        force_file = os.path.join(self.data_dir, f"ele_{tag}_force.out")
        deform_file = os.path.join(self.data_dir, f"ele_{tag}_deform.out")
        
        if not os.path.exists(force_file) or not os.path.exists(deform_file):
            self.info_label.setText("Error: Faltan archivos de resultados.")
            return

        try:
            # Helper to read numerical data
            def read_data(filepath):
                data = []
                with open(filepath, 'r') as f:
                    for line in f:
                        parts = line.split()
                        if not parts: continue
                        data.append([float(x) for x in parts])
                return data

            raw_forces = read_data(force_file)
            raw_deforms = read_data(deform_file)
            
            if not raw_forces:
                self.info_label.setText("El archivo de resultados está vacío.")
                return

            n_cols_f = len(raw_forces[0])
            n_cols_d = len(raw_deforms[0])
            
            # Remove time column count
            vals_f = n_cols_f - 1
            vals_d = n_cols_d - 1
            
            # Obtener puntos reales del elemento para calcular componentes
            manager = ProjectManager.instance()
            element = manager.get_element(tag)
            integration_points = getattr(element, 'integration_points', 5)

            # Evitar división por cero
            if integration_points <= 0: integration_points = 5

            comps_f = vals_f // integration_points
            comps_d = vals_d // integration_points
            

            self.info_label.setText(
                f"Datos cargados para Elemento {tag}.\n"
                f"Puntos Integración: {integration_points}\n"
                f"Comp. Fuerza: {comps_f} (P, M, V?)\n"
                f"Comp. Deform: {comps_d} (eps, kap, gam?)"
            )
            
            self.current_data = {
                "forces": raw_forces,
                "deforms": raw_deforms,
                "comps_f": comps_f,
                "comps_d": comps_d,
                "n_sections": integration_points
            }
            
        except Exception as e:
            self.info_label.setText(f"Error leyendo datos: {str(e)}")
            import traceback
            traceback.print_exc()

    def update_plot(self):
        if not hasattr(self, 'current_data'): 
            return

        # 0. Preparar conversion de unidades
        u_man = UnitManager.instance()

        sec_idx_combo = self.section_combo.currentData()
        if sec_idx_combo is None: sec_idx_combo = 1 
        sec_idx = sec_idx_combo - 1 

        forces = self.current_data["forces"]
        deforms = self.current_data["deforms"]
        
        # Recuperar componentes detectados (default a 3 si falla carga)
        n_comps_f = self.current_data.get("comps_f", 3)
        n_comps_d = self.current_data.get("comps_d", 3)

        # 1. Determinar Índice de columna para fuerza (Y Axis)
        y_type = self.y_axis_combo.currentIndex()

        if y_type == 0: # Momento (Mz)
            comp_offset_f = 1
            unit_type = UnitType.MOMENT
            label_base = "Momento"
            unit_label_y = u_man.get_current_unit(UnitType.MOMENT)
        elif y_type == 1: # Axial (P)
            comp_offset_f = 0
            unit_type = UnitType.FORCE
            label_base = "Axial"
            unit_label_y = u_man.get_current_unit(UnitType.FORCE)
        else: # Cortante (Vy)
            comp_offset_f = 2
            unit_type = UnitType.FORCE
            label_base = "Cortante"
            unit_label_y = u_man.get_current_unit(UnitType.FORCE)

        y_axis_text = f"{label_base} ({unit_label_y})"

        # CALCULO DINÁMICO DE COLUMNAS
        col_F = 1 + (sec_idx * n_comps_f) + comp_offset_f
        
        # 2. Determina indice de columna para deformación (Curvatura siempre es el segundo comp?)
        # Asumimos orden: eps, kappa (curvatura), gamma ??
        # Usualmente kappa es el segundo componente (offset 1)
        comp_offset_d = 1
        col_C = 1 + (sec_idx * n_comps_d) + comp_offset_d

        len_factor = u_man.to_base(1.0, UnitType.LENGTH) 
        unit_label_x = f"rad/{u_man.get_current_unit(UnitType.LENGTH)}" 

        if col_F >= len(forces[0]) or col_C >= len(deforms[0]):
            self.plot_widget.clear()
            self.plot_widget.setTitle(f"Error: Indices fuera de rango (F={col_F}, C={col_C})")
            return

        y_values = []
        x_values = []

        for row_f, row_d in zip(forces, deforms):
            # Valor crudo
            raw_y = row_f[col_F]
            raw_x = row_d[col_C]

            # Absoluto (Opcional, a veces es mejor ver el signo)
            abs_y = abs(raw_y)
            abs_x = abs(raw_x)

            # Conversión de unidades
            vis_y = u_man.from_base(abs_y, unit_type)
            vis_x = abs_x * len_factor

            y_values.append(vis_y)
            x_values.append(vis_x)

        # Asegurar origen
        if not x_values or x_values[0] != 0:
            x_values.insert(0, 0.0)
            y_values.insert(0, 0.0)

        # Graficar
        self.plot_widget.clear()
        pen = pg.mkPen(color='b', width=2)
        self.plot_widget.plot(x_values, y_values, pen=pen, name="Respuesta")

        self.plot_widget.setLabel('bottom', f"Curvatura ({unit_label_x})")
        self.plot_widget.setLabel('left', y_axis_text)
        self.plot_widget.setTitle(f"Sección {sec_idx_combo} - Elemento {self.element_combo.currentText()}")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getAxis('bottom').enableAutoSIPrefix(False)
        self.plot_widget.getAxis('left').enableAutoSIPrefix(False)
        
        if x_values:
            max_x = max(x_values)
            max_y = max(y_values)
            # Dar un margen del 10%
            self.plot_widget.setXRange(0, max_x * 1.1 if max_x > 0 else 1)
            self.plot_widget.setYRange(0, max_y * 1.1 if max_y > 0 else 1)