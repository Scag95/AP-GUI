from PyQt6.QtWidgets import QSpinBox
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QComboBox, QPushButton, QCheckBox)
from src.analysis.manager import ProjectManager
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitManager
from src.utils.units import UnitType

class PushoverDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
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

        #--- Formulario ---
        form_layout = QFormLayout()

        #1. Selector Nodo Control
        self.combo_node = QComboBox()
        self.populate_nodes()

        #2. Tipo de fuerzas
        self.combo_load_pattern_type = QComboBox()
        self.combo_load_pattern_type.addItems(["Modal","Uniforme"])


        #2. Desplazamiento Máximo
        self.spin_drift = UnitSpinBox(UnitType.LENGTH)
        self.spin_drift.setRange(0,100)
        self.spin_drift.setDecimals(3)
        self.spin_drift.setSingleStep(0.1)
        self.spin_drift.set_value_base(0.3) #Default 30cm
        
        #2.5 Número de pasos
        self.spin_steps = QSpinBox()
        self.spin_steps.setRange(0 , 100000)
        self.spin_steps.setSingleStep(500)
        self.spin_steps.setValue(1000)

        form_layout.addRow("Nodo de Control:",self.combo_node)
        form_layout.addRow("Desplazamiento Máx:", self.spin_drift)
        form_layout.addRow("Número de pasos:", self.spin_steps)
        form_layout.addRow("Modo de aplicación de fuerza", self.combo_load_pattern_type)
        
        layout.addLayout(form_layout)

        # 3. Checkbox Adaptativo
        self.chk_adaptive = QCheckBox("Análisis Adaptativo Secuencial (Freeze Forward)")
        self.chk_adaptive.setToolTip("Congela pisos que fallen (mecanismo) y continúa el análisis para evaluar pisos superiores.")
        form_layout.addRow("Estrategia:", self.chk_adaptive)

        # --- Selector de Método de Congelamiento ---
        from PyQt6.QtWidgets import QHBoxLayout, QLabel
        freeze_method_layout = QHBoxLayout()
        self.freeze_method_combo = QComboBox()
        self.freeze_method_combo.addItems(["Springs", "Node Fix (Anclaje Rígido)", "Load Pattern (Fuerzas Opuestas)"])
        self.freeze_method_combo.setToolTip("Elige cómo OpenSees tratará cinemáticamente a un piso que acaba de fallar.")

        freeze_method_layout.addWidget(self.freeze_method_combo)
        
        # Ocultar o mostrar según el checkbox adaptativo
        self.freeze_method_combo.setVisible(False)
        self.chk_adaptive.toggled.connect(self.freeze_method_combo.setVisible)

        form_layout.addRow("Método Congelamiento:", freeze_method_layout)

        # 3.5 Criterios de Fallo Personalizados
        from PyQt6.QtWidgets import QDoubleSpinBox, QGroupBox
        self.chk_custom_failure = QCheckBox("Personalizar Criterios de Fallo")
        self.chk_custom_failure.setToolTip("Modifica los límites de deriva y pérdida de resistencia espacial.")
        form_layout.addRow("Criterios de Fallo:", self.chk_custom_failure)

        # Contenedor para los parámetros (inicialmente oculto)
        self.failure_params_group = QGroupBox("Parámetros del Detector de Fallos")
        failure_layout = QFormLayout()
        self.failure_params_group.setLayout(failure_layout)
        
        self.spin_sensitivity = QDoubleSpinBox()
        self.spin_sensitivity.setRange(0, 100)
        self.spin_sensitivity.setSingleStep(1)
        self.spin_sensitivity.setDecimals(2)
        self.spin_sensitivity.setValue(1)
        self.spin_sensitivity.setSuffix(" %")
        self.spin_sensitivity.setToolTip("Porcentaje de la rigidez inicial para considerar 'plana' la curva (Mecanismo).")
        failure_layout.addRow("Sensibilidad de Caída (1-100%):", self.spin_sensitivity)

        self.spin_max_drift = QDoubleSpinBox()
        self.spin_max_drift.setRange(0.1, 100.0) # Normalmete del 0.1 al 20%
        self.spin_max_drift.setSingleStep(0.5)
        self.spin_max_drift.setDecimals(2)
        self.spin_max_drift.setValue(8.0) # 8% por defecto (Límite clásico)
        self.spin_max_drift.setSuffix(" %")
        self.spin_max_drift.setToolTip("Deriva relativa máxima permitida antes de declarar colapso estructural por planta.")
        failure_layout.addRow("Deriva Máxima de Piso:", self.spin_max_drift)

        self.failure_params_group.setVisible(False)
        form_layout.addRow(self.failure_params_group)

        self.chk_custom_failure.toggled.connect(self.failure_params_group.setVisible)
        
        # 4. Checkbox Ver Cargas
        self.chk_show_loads = QCheckBox("Visualizar distribución de cargas del análisis")
        self.chk_show_loads.setChecked(True) # Activado por defecto
        form_layout.addRow("Visualización:", self.chk_show_loads)

        # --- BOTONES ---
        # Run Button
        self.btn_run = QPushButton("Ejecutar Pushover")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.btn_run.clicked.connect(self.run_pushover)
        layout.addWidget(self.btn_run)



    def populate_nodes(self):
        nodes = self.manager.get_all_nodes()
        if not nodes: return
        sorted_nodes = sorted(nodes, key = lambda n: n.y, reverse =True)

        for n in sorted_nodes:
            self.combo_node.addItem(f"Nodo {n.tag} (Y={n.y:.2f})", userData=n.tag)

    
    def run_pushover(self):
        from src.analysis.opensees_translator import OpenSeesTranslator
        um = UnitManager.instance()

        #1. Obtenner inputs
        idx = self.combo_node.currentIndex()
        load_pattern_type = self.combo_load_pattern_type.currentText()
        if idx < 0: return
        control_node = self.combo_node.itemData(idx)
        max_disp = self.spin_drift.get_value_base()
        steps = self.spin_steps.value()


        #2. Instacniar Tranaltor y ejecutar
        translator = OpenSeesTranslator()

        # Reabrir archivo existente para que registre log de pushover
        try:
            translator.builder.debug_file = open("model_debug.py", "a", encoding="utf-8")
            translator.builder.debug_file.write("\n\n# ====== CONFIGURACION DE PUSHOVER ======\n")
        except Exception as e:
            print(f"Aviso: No se pudo reabrir model_debug.py ({e})")

        print(f"Lanzando Pushover: Node {control_node}, Disp {max_disp}, Pattern {load_pattern_type}")



        try: 
            #Ejecutar lógica backend
            results = None
            if self.chk_adaptive.isChecked():
                print("[UI] Ejecutando Pushover Adaptativo (Freeze Forward)...")
                
                # Extraer parámetros personalizados si aplica
                sen = self.spin_sensitivity.value() if self.chk_custom_failure.isChecked() else None
                drf = self.spin_max_drift.value() if self.chk_custom_failure.isChecked() else None
                
                # Extraer método de congelamiento escogido
                idx_method = self.freeze_method_combo.currentIndex()
                if idx_method == 0: freeze_method = "spring"
                elif idx_method == 1: freeze_method = "fix"
                else: freeze_method = "load"
                
                results = translator.run_adaptive_pushover(control_node, max_disp, steps, load_pattern_type, 
                                                           sensitivity=sen, freeze_method=freeze_method, max_drift = drf)
            else:
                print("[UI] Ejecutando Pushover Monotónico Normal...")
                results = translator.run_pushover_analysis(control_node, max_disp, steps, load_pattern_type)

            if results:
                # Guardar resultados en el Manager para persistencia
                self.manager.pushover_results = results
                
                # Activar la nueva barra de animación en la ventana principal
                if hasattr(self.parent(), 'toggle_animation_toolbar'):
                    self.parent().toggle_animation_toolbar(True)
                    
                # Mostrar cargas si se solicitó
                if hasattr(self.parent(), 'set_pushover_loads_visible'):
                    self.parent().set_pushover_loads_visible(self.chk_show_loads.isChecked())
                
                # Pasamos el diccionario crudo al dialog de resultados para la curva XY
                from src.ui.dialogs.pushover_result_dialog import PushoverResultsWidget
                
                # Pasamos también el estado inicial del checkbox para que el result_dialog arranque sincronizado
                widget = PushoverResultsWidget(results, self.chk_show_loads.isChecked())
                if hasattr(self.parent(), 'add_tool_window'):
                    self.parent().add_tool_window(widget,"Curva de Capacidad (Pushover)")


        except Exception as e:
            print(f"Error crítico en Pushover: {e}")
            import traceback
            traceback.print_exc()

