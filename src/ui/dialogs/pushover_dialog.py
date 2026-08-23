import os
import sys
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QSpinBox, QWidget
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QComboBox, QPushButton, QCheckBox, QProgressBar, QLabel, QTextEdit)
from PyQt6.QtWidgets import QApplication
from src.analysis.manager import ProjectManager
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitType


class OutputCapture(QObject):
    """Redirige sys.stdout hacia un QTextEdit vía señales de Qt."""
    text_written = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._original_stdout = None

    def write(self, text):
        if text:
            self.text_written.emit(text)

    def flush(self):
        pass

    def attach(self):
        self._original_stdout = sys.stdout
        sys.stdout = self

    def detach(self):
        if self._original_stdout is not None:
            sys.stdout = self._original_stdout
            self._original_stdout = None


class PushoverDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Análisis Pushover")
        self.resize(800, 700)

        # Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.manager = ProjectManager.instance()
        self._analysis_completed = False

        # Layout Principal
        layout = QVBoxLayout(self)

        # --- Formulario ---
        form_layout = QFormLayout()

        # 1. Selector Nodo Control
        self.combo_node = QComboBox()
        self.populate_nodes()

        # 2. Tipo de fuerzas
        self.combo_load_pattern_type = QComboBox()
        self.combo_load_pattern_type.addItems(["Modal", "Uniforme", "Patrón Definido"])
        self.combo_load_pattern_type.currentTextChanged.connect(self._on_load_type_changed)

        # Selector de patrón (visible únicamente cuando se elige "Patrón Definido")
        self.combo_defined_pattern = QComboBox()
        self.combo_defined_pattern.setMinimumWidth(200)
        self.combo_defined_pattern.setToolTip("Usa las cargas nodales de este patrón como distribución lateral")
        for p in self.manager.get_all_patterns():
            nodal_fx = [l for l in p.loads if hasattr(l, 'fx') and abs(l.fx) > 1e-9]
            if nodal_fx:  # Solo mostrar patrones que tengan cargas nodales en X
                self.combo_defined_pattern.addItem(f"Patrón {p.tag}: {p.name}", p.tag)
        self.combo_defined_pattern.setVisible(False)

        # 2. Desplazamiento Máximo
        self.spin_drift = UnitSpinBox(UnitType.LENGTH)
        self.spin_drift.setRange(0, 100)
        self.spin_drift.setDecimals(3)
        self.spin_drift.setSingleStep(0.1)
        self.spin_drift.set_value_base(1)  # Default 100cm

        # 2.5 Número de pasos
        self.spin_steps = QSpinBox()
        self.spin_steps.setRange(0, 100000)
        self.spin_steps.setSingleStep(500)
        self.spin_steps.setValue(3000)

        form_layout.addRow("Nodo de Control:", self.combo_node)
        form_layout.addRow("Desplazamiento Máx:", self.spin_drift)
        form_layout.addRow("Número de pasos:", self.spin_steps)
        form_layout.addRow("Modo de aplicación de fuerza", self.combo_load_pattern_type)
        form_layout.addRow("Patrón lateral a usar:", self.combo_defined_pattern)

        # Guardar referencia al label del combo de patrón para ocultar/mostrar la fila completa
        self._label_defined_pattern = form_layout.labelForField(self.combo_defined_pattern)
        if self._label_defined_pattern:
            self._label_defined_pattern.setVisible(False)

        layout.addLayout(form_layout)

        # 3. Checkbox Adaptativo
        self.chk_adaptive = QCheckBox("Análisis Adaptativo Secuencial (Freeze Forward)")
        self.chk_adaptive.setToolTip("Congela pisos que fallen (mecanismo) y continúa el análisis para evaluar pisos superiores.")
        form_layout.addRow("Estrategia:", self.chk_adaptive)

        # --- Selector de Método de Congelamiento ---
        from PyQt6.QtWidgets import QHBoxLayout, QLabel
        freeze_method_layout = QHBoxLayout()
        self.freeze_method_combo = QComboBox()
        self.freeze_method_combo.addItems(["Cruces de San Andrés", "Springs", "Node Fix (Anclaje Rígido)", "Load Pattern (Fuerzas Opuestas)"])
        self.freeze_method_combo.setToolTip("Elige cómo OpenSees tratará cinemáticamente a un piso que acaba de fallar.")
        self.freeze_method_combo.currentIndexChanged.connect(self._on_freeze_method_changed)

        freeze_method_layout.addWidget(self.freeze_method_combo)

        # Ocultar o mostrar según el checkbox adaptativo
        self.freeze_method_combo.setVisible(False)
        self.chk_adaptive.toggled.connect(self._on_adaptive_toggled)

        form_layout.addRow("Método Congelamiento:", freeze_method_layout)

        # --- Checkboxes de Cruces de San Andrés (solo visibles para crosses) ---
        self.cross_options_widget = QWidget()
        cross_options_layout = QHBoxLayout(self.cross_options_widget)
        cross_options_layout.setContentsMargins(0, 0, 0, 0)

        self.chk_cross_beams = QCheckBox("Generar cruces en vigas")
        self.chk_cross_beams.setToolTip("Añade elementos Truss horizontales entre nodos del mismo piso")
        self.chk_cross_columns = QCheckBox("Generar cruces en columnas")
        self.chk_cross_columns.setToolTip("Añade elementos Truss verticales entre nodos de columnas")

        cross_options_layout.addWidget(self.chk_cross_beams)
        cross_options_layout.addWidget(self.chk_cross_columns)
        cross_options_layout.addStretch()

        self.cross_options_widget.setVisible(False)
        form_layout.addRow(self.cross_options_widget)

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
        self.spin_sensitivity.setRange(-100, 100)
        self.spin_sensitivity.setSingleStep(1)
        self.spin_sensitivity.setDecimals(2)
        self.spin_sensitivity.setValue(-0.05)
        self.spin_sensitivity.setSuffix(" %")
        self.spin_sensitivity.setToolTip("Porcentaje de la rigidez inicial para considerar 'plana' la curva (Mecanismo).")
        failure_layout.addRow("Sensibilidad de Caída (-100% a 100%):", self.spin_sensitivity)

        self.spin_max_drift = QDoubleSpinBox()
        self.spin_max_drift.setRange(0.1, 100.0)  # Normalmente del 0.1 al 20%
        self.spin_max_drift.setSingleStep(0.5)
        self.spin_max_drift.setDecimals(2)
        self.spin_max_drift.setValue(8.0)  # 8% por defecto (Límite clásico)
        self.spin_max_drift.setSuffix(" %")
        self.spin_max_drift.setToolTip("Deriva relativa máxima permitida antes de declarar colapso estructural por planta.")
        failure_layout.addRow("Deriva Máxima de Piso:", self.spin_max_drift)

        self.failure_params_group.setVisible(False)
        form_layout.addRow(self.failure_params_group)

        self.chk_custom_failure.toggled.connect(self.failure_params_group.setVisible)

        # 4. Checkbox Ver Cargas
        self.chk_show_loads = QCheckBox("Visualizar distribución de cargas del análisis")
        self.chk_show_loads.setChecked(True)  # Activado por defecto
        form_layout.addRow("Visualización:", self.chk_show_loads)

        # --- BOTONES ---
        self.btn_run = QPushButton("Ejecutar Pushover")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.btn_run.clicked.connect(self.run_pushover)
        layout.addWidget(self.btn_run)

        # --- PROGRESO ---
        self.lbl_progress = QLabel("Ejecutando análisis...")
        self.lbl_progress.setVisible(False)
        layout.addWidget(self.lbl_progress)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # --- TERMINAL DE SALIDA ---
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setPlaceholderText("Salida del análisis aparecerá aquí...")
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #3e3e3e;
                padding: 6px;
            }
        """)
        self.terminal.setMinimumHeight(150)
        layout.addWidget(self.terminal)

        # Forzar actualización inicial del estado de cruces
        self._on_freeze_method_changed(self.freeze_method_combo.currentIndex())

    def _on_load_type_changed(self, text):
        """Muestra u oculta el selector de patrón según el modo elegido."""
        is_defined = (text == "Patrón Definido")
        self.combo_defined_pattern.setVisible(is_defined)
        if self._label_defined_pattern:
            self._label_defined_pattern.setVisible(is_defined)

    def _on_adaptive_toggled(self, checked):
        """Muestra u oculta el combo de método y las opciones de cruces."""
        self.freeze_method_combo.setVisible(checked)
        if checked:
            self._on_freeze_method_changed(self.freeze_method_combo.currentIndex())
        else:
            if hasattr(self, 'cross_options_widget'):
                self.cross_options_widget.setVisible(False)

    def _on_freeze_method_changed(self, idx):
        """Muestra u oculta las opciones de Cruces de San Andrés."""
        if not hasattr(self, 'cross_options_widget'):
            return
        is_crosses = (self.freeze_method_combo.currentText() == "Cruces de San Andrés")
        self.cross_options_widget.setVisible(is_crosses)

    def populate_nodes(self):
        nodes = self.manager.get_all_nodes()
        if not nodes:
            return
        sorted_nodes = sorted(nodes, key=lambda n: n.y, reverse=True)

        for n in sorted_nodes:
            self.combo_node.addItem(f"Nodo {n.tag} (Y={n.y:.2f})", userData=n.tag)

    def _append_terminal(self, text):
        """Inserta texto en la terminal y hace scroll al final."""
        self.terminal.insertPlainText(text)
        scrollbar = self.terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        QApplication.processEvents()

    def _set_completed_state(self):
        """Cambia la UI al estado 'análisis completado': botón Cerrar, guarda log."""
        self._analysis_completed = True
        self.manager.pushover_log_text = self.terminal.toPlainText()
        self.btn_run.setText("Cerrar")
        self.btn_run.setStyleSheet("background-color: #757575; color: white; font-weight: bold; padding: 10px;")
        self.btn_run.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.lbl_progress.setText("Análisis completado exitosamente")
        self.lbl_progress.setVisible(True)
        self._append_terminal("\n[UI] Análisis finalizado. Puedes revisar los logs arriba.\n")

    def run_pushover(self):
        # Si ya terminó, el botón actúa como Cerrar
        if self._analysis_completed:
            self.accept()
            return

        from src.analysis.opensees_translator import OpenSeesTranslator

        # 1. Obtener inputs
        idx = self.combo_node.currentIndex()
        load_pattern_type = self.combo_load_pattern_type.currentText()
        if idx < 0:
            return
        control_node = self.combo_node.itemData(idx)
        max_disp = self.spin_drift.get_value_base()
        steps = self.spin_steps.value()

        # Tag del patrón definido (solo relevante cuando load_pattern_type == "Patrón Definido")
        defined_pattern_tag = None
        if load_pattern_type == "Patrón Definido":
            defined_pattern_tag = self.combo_defined_pattern.currentData()
            if defined_pattern_tag is None:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Aviso", "No hay ningún patrón con cargas laterales disponible.\nCrea primero un patrón con NodalLoad en la dirección X.")
                return

        # 2. Instanciar Translator y ejecutar
        translator = OpenSeesTranslator()

        # Reabrir archivo existente para que registre log de pushover
        try:
            debug_path = os.path.join("tests", "model_debug.py") if os.path.exists("tests") else "model_debug.py"
            translator.builder.debug_file = open(debug_path, "a", encoding="utf-8")
            translator.builder.debug_file.write("\n\n# ====== CONFIGURACION DE PUSHOVER ======\n")
        except Exception as e:
            self._append_terminal(f"Aviso: No se pudo reabrir model_debug.py ({e})\n")

        # Activar barra de progreso y limpiar terminal
        self.btn_run.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.lbl_progress.setVisible(True)
        self.terminal.clear()
        QApplication.processEvents()

        def on_progress(current, total, round_idx=0, total_rounds=1):
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            if total_rounds > 1:
                self.lbl_progress.setText(f"Ronda {round_idx + 1} de {total_rounds} | Paso {current} / {total}")
            else:
                self.lbl_progress.setText(f"Ejecutando análisis... Paso {current} / {total}")
            QApplication.processEvents()

        # Capturar stdout hacia la terminal
        capture = OutputCapture()
        capture.text_written.connect(self._append_terminal)
        capture.attach()

        try:
            self._append_terminal(f"Lanzando Pushover: Node {control_node}, Disp {max_disp}, Pattern {load_pattern_type}\n")

            # Ejecutar lógica backend
            results = None
            if self.chk_adaptive.isChecked():
                self._append_terminal("[UI] Ejecutando Pushover Adaptativo (Freeze Forward)...\n")

                # Extraer parámetros personalizados si aplica
                sen = self.spin_sensitivity.value()
                drf = self.spin_max_drift.value()

                # Extraer método de congelamiento escogido
                idx_method = self.freeze_method_combo.currentIndex()
                if idx_method == 0:
                    freeze_method = "crosses"
                elif idx_method == 1:
                    freeze_method = "spring"
                elif idx_method == 2:
                    freeze_method = "fix"
                else:
                    freeze_method = "load"

                cross_beams = self.chk_cross_beams.isChecked()
                cross_columns = self.chk_cross_columns.isChecked()

                results = translator.run_adaptive_pushover(
                    control_node, max_disp, steps, load_pattern_type,
                    sensitivity=sen, freeze_method=freeze_method, max_drift=drf,
                    defined_pattern_tag=defined_pattern_tag,
                    progress_callback=on_progress,
                    cross_beams=cross_beams, cross_columns=cross_columns
                )
            else:
                self._append_terminal("[UI] Ejecutando Pushover Monotónico Normal...\n")
                results = translator.run_pushover_analysis(
                    control_node, max_disp, steps, load_pattern_type,
                    defined_pattern_tag=defined_pattern_tag,
                    progress_callback=on_progress
                )

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
                    self.parent().add_tool_window(widget, "Curva de Capacidad (Pushover)")

                # NO cerrar el diálogo; cambiar a estado completado
                self._set_completed_state()

        except Exception as e:
            self._append_terminal(f"Error crítico en Pushover: {e}\n")
            import traceback
            self._append_terminal(traceback.format_exc())
            self.btn_run.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.lbl_progress.setVisible(False)

        finally:
            capture.detach()
