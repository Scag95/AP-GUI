from PyQt6.QtWidgets import QToolBar, QSlider, QLabel, QWidget, QHBoxLayout, QSizePolicy, QCheckBox, QApplication
from PyQt6.QtCore import Qt
from src.analysis.manager import ProjectManager

class AnimationToolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__("Animación Pushover", parent)
        self.manager = ProjectManager.instance()
        self.parent_window = parent

        # Label State
        self.step_label = QLabel("Paso de Animación: (No disponible)")
        self.step_label.setStyleSheet("padding: 0 10px; font-weight: bold;")
        
        # Slider
        self.step_slider = QSlider(Qt.Orientation.Horizontal)
        self.step_slider.setMinimum(0)
        self.step_slider.setEnabled(False)
        self.step_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.step_slider.setMinimumWidth(300)

        # Checkbox "Sincronizar gráficas"
        self.chk_sync = QCheckBox("Sincronizar gráficas")
        self.chk_sync.setToolTip("Sincroniza este paso temporal con el visualizador M-Curvatura si está abierto.")

        # Widget Contenedor (para alinear a la derecha/centro)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.step_label)
        layout.addWidget(self.step_slider)
        layout.addWidget(self.chk_sync)

        self.addWidget(container)

        # Conectar el slider
        self.step_slider.valueChanged.connect(self._on_slider_changed)

    def load_pushover_results(self):
        """Carga los resultados cacheados en el manager al slider"""
        if hasattr(self.manager, 'pushover_results') and self.manager.pushover_results:
            node_disps = self.manager.pushover_results.get("node_displacements", [])
            if node_disps:
                self.step_slider.setMaximum(len(node_disps) - 1)
                self.step_slider.setValue(0)
                self.step_slider.setEnabled(True)
                self.step_label.setText("Animación Activa: Mueva el control deslizante")
                return True
        
        # Deshabilitar si no hay nada
        self.step_slider.setEnabled(False)
        self.step_label.setText("Paso de Animación: (No disponible)")
        return False

    def _on_slider_changed(self, value):
        self.step_label.setText(f"Paso de Animación: ({value})")
        if hasattr(self.manager, 'pushover_results') and self.manager.pushover_results:
            node_disps = self.manager.pushover_results.get("node_displacements", [])
            if 0 <= value < len(node_disps):
                step_data = node_disps[value]
                # Enviar solo a la ventana activa
                if self.parent_window and hasattr(self.parent_window, 'viz_widget'):
                    active_viz = self.parent_window.viz_widget
                    if active_viz:
                        active_viz.draw_kinematic_step(step_data)
                
                # Sincronizar dialogos si está activo
                if self.chk_sync.isChecked():
                    for widget in QApplication.instance().topLevelWidgets():
                        title = widget.windowTitle()
                        if title in ["Resultados de Sección: Momento-Curvatura", "Análisis Pushover"]:
                            try:
                                if hasattr(widget, 'slider_step'):
                                    dest_slider = widget.slider_step
                                    safe_val = max(dest_slider.minimum(), min(value + 1, dest_slider.maximum()))
                                    dest_slider.setValue(safe_val)
                            except Exception as e:
                                print(f"Error sincronizando grafica en {title}: {e}")
