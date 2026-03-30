from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from src.ui.dialogs.grid_dialog import gridDialog
from src.ui.dialogs.self_weight_dialog import SelfWeightDialog

class ToolsMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__("Herramientas", parent)
        self.main_window = parent

        #Grid
        grid_action = QAction("Generar Pórtico 2D", self)
        grid_action.triggered.connect(self.show_grid_dialog)
        self.addAction(grid_action)

        #Submenú: Cargas
        self.loads_menu = QMenu("Generación de Cargas", self)
        self.addMenu(self.loads_menu)
        
        #Acción Peso propio
        self.action_self_weight = QAction("Generar Peso Propio")
        self.action_self_weight.setStatusTip("Calcula y aplica cargas distribuidas en la sección y material")

        self.action_self_weight.triggered.connect(self.open_self_weight_dialog)
        self.loads_menu.addAction(self.action_self_weight)

    def open_self_weight_dialog(self):
        dialog = SelfWeightDialog(self.main_window)
        dialog.exec()

    def show_grid_dialog(self):
        dialog = gridDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            generator = FrameGenerator()
            try:
                generator.generate_2d_frame(
                    stories= data["stories"],
                    bays=data["bays"],
                    story_height=data["story_height"],
                    bay_width=data["bay_width"],
                    beam_sec_tag=data["beam_sec_tag"],
                    col_sec_tag=data["col_sec_tag"],
                    integration_points=data["integration_points"],
                    add_base_beams=data["add_base_beams"]

                )
                QMessageBox.information(self, "Exito","Portico generado correctamente")
                parent_window = self.parent()
                if hasattr(parent_window, 'viz_widget'):
                    parent_window.viz_widget.refresh_viz()
            except Exception as e:
                print(str(e))
                QMessageBox.critical(self, "Error", f"Error generando pórtico: {str(e)}")

