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

        self.act_clear = QAction("Ocultar Diagramas", self)
        self.act_clear.triggered.connect(lambda: self._show_diagram(None))
        self.results_menu.addAction(self.act_clear)

    


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

                # Debug: Mostrar en consola para verificar
                print("[DEBUG] [Resultados obtenidos]")
                print(f"Nodos con desplazamiento: {len(results['displacements'])}")
                
                # Visualizar en el Graph Widget
                if self.parent() and hasattr(self.parent(), "viz_widget"):
                    # Pasamos el objeto results COMPLETO
                    self.parent().viz_widget.show_deformation(results)

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
        dlg = PushoverDialog(self.parent())
        dlg.exec()

    def _show_curve_pushover(self):
        dlg = PushoverResultsDialog(self.parent())
        dlg.exec()

    def _show_section_results(self):
        dlg = MomentCurvatureDialog(self.parent())
        dlg.exec()
