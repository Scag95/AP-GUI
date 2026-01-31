from PyQt6.QtWidgets import QMessageBox
from src.analysis.opensees_translator import OpenSeesTranslator
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction



class AnalyzeMenu(QMenu):
    def __init__(self, parent = None):
        super().__init__("Analizar",parent)
        self.action_gravity = QAction("Ejecutar Análisis de Gravedad",self)
        self.action_gravity.setStatusTip("Construye el modelo y ejecuta un análisis estático lineal")
        self.action_gravity.triggered.connect(self.run_gravity)
        self.addAction(self.action_gravity)

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
                print("\n--- DESPLAZAMIENTOS ---")
                for node_tag, disp in results["displacements"].items():
                    dx, dy, rz = disp
                    if abs(dx) > 1e-9 or abs(dy) > 1e-9: # Filtro de ceros
                        print(f"Nodo {node_tag}: dx={dx:.6e}, dy={dy:.6e}")

                # Visualizar en el Graph Widget
                # Asumimos que parent() es MainWindow y tiene el atributo viz_widget
                if self.parent() and hasattr(self.parent(), "viz_widget"):
                    # Factor de escala fijo por ahora (100x)
                    self.parent().viz_widget.show_deformation(results["displacements"])

            if results['displacements']:
                first_node = list(results['displacements'].keys())[0]
                print(f"Nodo {first_node} Disp:{results['displacements'][first_node]}")
                QMessageBox.information(self, "Análisis Completado", "El análisis finalizó correctamente.")
            else:
                QMessageBox.warning(self, "Error de análisis")

        except Exception as e:
            QMessageBox.critical(self, "Error crítico," f"Ocurrio error inesperado \n{str(e)}")
            print(e)
