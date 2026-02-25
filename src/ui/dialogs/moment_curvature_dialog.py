from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QFrame, QListWidget, QListWidgetItem, QAbstractItemView, QSlider)
from PyQt6.QtCore import Qt
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
        controls_layout.setContentsMargins(10, 10, 10, 10)
        controls_layout.setSpacing(10)

        # 1. Element Selector
        controls_layout.addWidget(QLabel("Seleccionar Elemento:"))
        self.element_combo = QComboBox()
        self.element_combo.currentIndexChanged.connect(self._on_element_changed)
        controls_layout.addWidget(self.element_combo)

        # 2. Variable Selector (Y Axis)
        controls_layout.addWidget(QLabel("<b>2. Variable Eje Y:</b>"))
        self.y_axis_combo = QComboBox()
        self.y_axis_combo.addItems(["Momento (Mz)", "Fuerza Axial (P)", "Cortante (Vy)"])
        self.y_axis_combo.currentIndexChanged.connect(self.update_plot)
        controls_layout.addWidget(self.y_axis_combo)

        # 3. Section Selector (Multi-select List)
        controls_layout.addWidget(QLabel("<b>3. Secciones a Graficar:</b>"))
        self.section_list = QListWidget()
        self.section_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection) # Solo check boxes
        self.section_list.itemChanged.connect(self.update_plot)
        controls_layout.addWidget(self.section_list)

        # Info Box
        self.info_label = QLabel("Seleccione un elemento para ver sus resultados.")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #555; font-size: 11px; margin-top: 10px;")
        controls_layout.addWidget(self.info_label)

        main_layout.addWidget(controls_frame)

        # --- Right Panel: Plot ---
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', "Curvatura (rad/m)")
        self.plot_widget.setLabel('left', "Momento (Nm)")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Desactivar auto-escalado SI permanentemente
        self.plot_widget.getAxis('bottom').enableAutoSIPrefix(False)
        self.plot_widget.getAxis('left').enableAutoSIPrefix(False)
        self.plot_widget.addLegend(offset=(30,30))

        # Slider para animar pasos
        slider_layout = QHBoxLayout()
        self.lbl_step = QLabel("Paso: Todos")
        self.slider_step = QSlider(Qt.Orientation.Horizontal)
        self.slider_step.setMinimum(1)
        self.slider_step.valueChanged.connect(self._on_slider_changed)
        
        slider_layout.addWidget(self.lbl_step)
        slider_layout.addWidget(self.slider_step)

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.plot_widget, 1)
        plot_layout.addLayout(slider_layout)

        main_layout.addLayout(plot_layout, 1)
        
        self.current_step_val = None

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

    def _on_slider_changed(self, value):
        self.current_step_val = value
        self.update_plot()

    def _on_element_changed(self):
        ele_tag = self.element_combo.currentData()
        if ele_tag is None: return
        
        manager = ProjectManager.instance()
        element = manager.get_element(ele_tag)

        if element is None:
            self.info_label.setText(f"Error: Elemento {ele_tag} no encontrado en proyecto.")
            self.plot_widget.clear()
            return

        # Cargar datos desde disco
        self.load_element_data(ele_tag)
        
        # Configurar puntos de integración
        num_points = getattr(element, 'integration_points')

        self.section_list.blockSignals(True)
        self.section_list.clear()

        for i in range(1, num_points + 1):
            item_text = f"Sección {i}"
            if i == 1: item_text += " (Inicio/Base)"
            elif i == num_points: item_text += " (Fin/Tope)"
            
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)   
            item.setData(Qt.ItemDataRole.UserRole, i) #Guarda inidice real (1-based)

            #Por defecto SOLO activar la Sección 1
            if i == 1:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            
            self.section_list.addItem(item)
        
        self.section_list.blockSignals(False)
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
            integration_points = getattr(element, 'integration_points')

            comps_f = vals_f // integration_points
            comps_d = vals_d // integration_points
            

            self.info_label.setText(
                f"Datos cargados para Elemento {tag}.\n"
                f"Columnas Datos: {vals_f}\n"
                f"Secciones Detectadas: {integration_points}"
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

        self.plot_widget.clear()

        # 0. Preparar conversion de unidades
        u_man = UnitManager.instance()
        forces = self.current_data["forces"]
        deforms = self.current_data["deforms"]
        n_comps_f = self.current_data["comps_f"]
        n_comps_d = self.current_data["comps_d"]
        
        max_steps = len(forces)
        
        self.slider_step.blockSignals(True)
        if self.slider_step.maximum() != max_steps:
            self.slider_step.setMaximum(max_steps)
            if self.current_step_val is None or self.current_step_val > max_steps:
                self.slider_step.setValue(max_steps)
                self.current_step_val = max_steps
        self.slider_step.blockSignals(False)
        
        if self.current_step_val == max_steps:
            self.lbl_step.setText(f"Paso: Todos ({max_steps})")
        else:
            self.lbl_step.setText(f"Paso: {self.current_step_val} / {max_steps}")

        # 1. Determinar Índice de columna para fuerza (Y Axis)
        y_type = self.y_axis_combo.currentIndex()
        if y_type == 0: # Momento (Mz)
            comp_offset_f = 1
            unit_type = UnitType.MOMENT
            label_base = "Momento"
        elif y_type == 1: # Axial (P)
            comp_offset_f = 0
            unit_type = UnitType.FORCE
            label_base = "Axial"
        else: # Cortante (Vy)
            comp_offset_f = 2
            unit_type = UnitType.FORCE
            label_base = "Cortante"
        unit_label_y = u_man.get_current_unit(unit_type)
        y_axis_text = f"{label_base} ({unit_label_y})"


        
        # 2. Determina indice de columna para deformación
        comp_offset_d = 1
        len_factor = u_man.to_base(1.0, UnitType.LENGTH) 

        unit_label_x = f"rad/{u_man.get_current_unit(UnitType.LENGTH)}" 

        self.plot_widget.setLabel('bottom', f"Curvatura ({unit_label_x})")
        self.plot_widget.setLabel('left', y_axis_text)

        # 3. Iterrar sobre secciones marcadas y graficar
        plotted_something = False
        all_x_max = 0
        all_y_max = 0

        #Obtener items de la lista
        count = self.section_list.count()

        for i in range(count):
            item = self.section_list.item(i)
            if item.checkState() != Qt.CheckState.Checked:
                continue
            
            sec_num = item.data(Qt.ItemDataRole.UserRole)

            # CALCULO DINÁMICO DE COLUMNAS
            col_F = 1 + ((sec_num - 1) * n_comps_f) + comp_offset_f
            col_C = 1 + ((sec_num - 1) * n_comps_d) + comp_offset_d

            if col_F >= len(forces[0]) or col_C >= len(deforms[0]):
                self.plot_widget.setTitle(f"Error: Indices fuera de rango para la Sección {sec_num}")
                continue

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

            # Recortar hasta el paso seleccionado
            limit = self.current_step_val
            x_plot = x_values[:limit]
            y_plot = y_values[:limit]

            # Graficar
            color = pg.intColor(i, hues=count, alpha=200)

            name_legend = f"Sección {sec_num}"

            if x_plot and y_plot:
                self.plot_widget.plot(x_plot, y_plot, pen=pg.mkPen(color, width=2), name=name_legend)
                # Punto líder para rastrear la animación
                self.plot_widget.plot([x_plot[-1]], [y_plot[-1]], pen=None, symbol='o', symbolBrush=color, symbolSize=8)
                
            self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
            plotted_something = True

            if x_values: 
                local_max_x = max([abs(x) for x in x_values])
                local_max_y = max([abs(y) for y in y_values])
                all_x_max = max(all_x_max, local_max_x)
                all_y_max = max(all_y_max, local_max_y)
            
        if plotted_something:
            self.plot_widget.setTitle(f"Elemento {self.element_combo.currentText()}")
            # Configurar rango usando EL MAXIMO GLOBAL DETECTADO
            margin = 1.1
            if all_x_max > 0:
                self.plot_widget.setXRange(0, all_x_max * margin)
            if all_y_max > 0:
                self.plot_widget.setYRange(0, all_y_max * margin)
        else:
            self.plot_widget.setTitle("Seleccione al menos una sección")
