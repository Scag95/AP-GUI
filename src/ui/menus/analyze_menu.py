from PyQt6.QtWidgets import QMessageBox
from src.analysis.opensees_translator import OpenSeesTranslator
from src.ui.dialogs.pushover_dialog import PushoverDialog
from src.ui.dialogs.pushover_result_dialog import PushoverResultsDialog
from src.ui.dialogs.moment_curvature_dialog import MomentCurvatureDialog
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction



class AnalyzeMenu(QMenu):
    def __init__(self, parent = None):
        super().__init__("Analizar",parent)
        
        # Acción Principal: Ejecutar Gravedad
        self.action_gravity = QAction("Ejecutar Análisis de Gravedad",self)
        self.action_gravity.setShortcut("F5")
        self.action_gravity.setStatusTip("Construye el modelo y ejecuta un análisis estático lineal")
        self.action_gravity.triggered.connect(self.run_gravity)
        self.addAction(self.action_gravity)
        # Modal Analysis
        self.action_modal = QAction("Análisis modal", self)
        self.action_modal.triggered.connect(self.run_modal)
        self.addAction(self.action_modal)

        # Pushover
        self.addAction("Análisis Pushover (No Lineal)", self.show_pushover_dialog)

        self.addSeparator()

        # Submenú de Resultados
        self.results_menu = QMenu("Ver Resultados", self)
        self.addMenu(self.results_menu)

        # Acciones de Visualización
        self.act_deform = QAction("Deformada", self)
        self.act_deform.triggered.connect(lambda: self._set_deformed_visibility(True))
        self.results_menu.addAction(self.act_deform)

        self.results_menu.addSeparator()

        # Acciones de Diagramas
        self.act_moment = QAction("Momentos (M)", self)
        self.act_moment.triggered.connect(lambda: self._show_diagram("M"))
        self.results_menu.addAction(self.act_moment)

        self.act_shear = QAction("Cortantes (V)", self)
        self.act_shear.triggered.connect(lambda: self._show_diagram("V"))
        self.results_menu.addAction(self.act_shear)

        self.act_axial = QAction("Axiales (P)", self)
        self.act_axial.triggered.connect(lambda: self._show_diagram("P"))
        self.results_menu.addAction(self.act_axial)

        self.pushover_curve = QAction("Curva Pushover",self)
        self.pushover_curve.triggered.connect(lambda: self._show_curve_pushover())
        self.results_menu.addAction(self.pushover_curve)

        self.section_results = QAction("Análisis de Sección (M-phi)", self)
        self.section_results.triggered.connect(lambda: self._show_section_results())
        self.results_menu.addAction(self.section_results)

        self.results_menu.addSeparator()

        self.act_clear = QAction("Ocultar Resultados", self)
        self.act_clear.triggered.connect(self._clear_results)
        self.results_menu.addAction(self.act_clear)

    def _set_deformed_visibility(self, visible):
        if self.parent() and hasattr(self.parent(), "viz_widget"):
            self.parent().viz_widget.set_visibility("deformed", visible)

    def _clear_results(self):
        if self.parent() and hasattr(self.parent(), "_viewports"):
            for viz in self.parent()._viewports:
                viz.show_force_diagrams(None)
                viz.set_visibility("deformed", False)

    def _show_diagram(self, type_):
        if self.parent() and hasattr(self.parent(), "viz_widget"):
            self.parent().viz_widget.show_force_diagrams(type_)

    def run_gravity(self):
        #1. Instancia al traductor
        translator = OpenSeesTranslator()

        try:
            #2. Construye el modelo
            translator.build_model()
            
            #3. Ejecuta el análisis
            success = translator.run_gravity_analysis()
            
            if success:
                #4. Obtener resultados 
                results = translator.get_analysis_results()
                
                # Guardar resultados globalmente
                from src.analysis.manager import ProjectManager
                ProjectManager.instance().gravity_results = results

                # Debug: Mostrar en consola para verificar
                print("[DEBUG] [Resultados obtenidos]")
                print(f"Nodos con desplazamiento: {len(results['displacements'])}")
                
                # Visualizar en el Graph Widget
                if self.parent() and hasattr(self.parent(), "broadcast_results"):
                    # Pasamos el objeto results COMPLETO
                    self.parent().broadcast_results(results)

                QMessageBox.information(self, "Análisis Completado", "El análisis finalizó correctamente.")
            else:
                QMessageBox.warning(self, "Error de análisis", "El análisis de gravedad falló en OpenSees.")

        except Exception as e:
            QMessageBox.critical(self, "Error crítico", f"Ocurrió error inesperado:\n{str(e)}")
            print(e)

    def run_modal(self):
        translator = OpenSeesTranslator()
        translator.run_modal_analysis(1)


    def show_pushover_dialog(self):
        from src.analysis.manager import ProjectManager
        if not ProjectManager.instance().gravity_results:
            reply = QMessageBox.warning(self, "Análisis Requerido", 
                                        "Es necesario ejecutar el análisis de gravedad antes de iniciar el Pushover para inicializar correctamente el estado estructural en OpenSees.\n\n¿Desea ejecutar el análisis de gravedad ahora?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.run_gravity()
                # Verificar si tras el intento realmente se logró
                if not ProjectManager.instance().gravity_results:
                    return
            else:
                return

        dlg = PushoverDialog(self.parent())
        dlg.exec()

    def _show_curve_pushover(self):
        from src.analysis.manager import ProjectManager
        results = ProjectManager.instance().pushover_results
        
        if not results:
             QMessageBox.warning(self, "No hay resultados", "Debe ejecutar primero un Análisis Pushover desde el menú Analizar.")
             return

        self._pushover_results_dlg = PushoverResultsDialog(results, self.parent())
        self._pushover_results_dlg.show()

    def _show_section_results(self):
        self._mc_dlg = MomentCurvatureDialog(self.parent())
        self._mc_dlg.show()
