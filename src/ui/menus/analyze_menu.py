from PyQt6.QtWidgets import QMessageBox, QMenu
from src.analysis.opensees_translator import OpenSeesTranslator
from src.ui.dialogs.pushover_dialog import PushoverDialog
from src.analysis.manager import ProjectManager
from PyQt6.QtGui import QAction


class AnalyzeMenu(QMenu):
    def __init__(self, parent = None):
        super().__init__("Analizar",parent)
        
        self.action_gravity = QAction("Ejecutar Análisis de Gravedad",self)
        self.action_gravity.setShortcut("F5")
        self.action_gravity.setStatusTip("Construye el modelo y ejecuta un análisis estático lineal")
        self.action_gravity.triggered.connect(self.run_gravity)
        self.addAction(self.action_gravity)

        self.action_modal = QAction("Análisis modal", self)
        self.action_modal.triggered.connect(self.run_modal)
        self.addAction(self.action_modal)

        self.addAction("Análisis Pushover (No Lineal)", self.show_pushover_dialog)

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
