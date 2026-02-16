from PyQt6.QtWidgets import QMessageBox
from src.analysis.frame_generator import FrameGenerator
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from src.ui.dialogs.material_dialog import MaterialDialog
from src.ui.dialogs.section_dialog import SectionDialog
from src.ui.dialogs.grid_dialog import gridDialog


class DefineMenu(QMenu):
    def __init__(self,parent=None):
        super().__init__("Definir",parent)
        self.setup_actions()

    def setup_actions(self):
        #Materiales
        self.action_materials = QAction("Materiales",self)
        #Conectar el boton con material_dialog
        self.action_materials.triggered.connect(self.open_material_dialog)
        self.addAction(self.action_materials)

        #Secciones
        self.action_sections = QAction("Secciones",self)
        #Conectar el boton con section_dialog
        self.action_sections.triggered.connect(self.open_section_dialog)
        self.addAction(self.action_sections)

        #Grid
        grid_action = QAction("Generar Pórtico 2D", self)
        grid_action.triggered.connect(self.show_grid_dialog)
        self.addAction(grid_action)
        
    def open_material_dialog(self):
        dlg = MaterialDialog(self)
        dlg.exec()

    def open_section_dialog(self):
        dlg = SectionDialog(self)
        dlg.exec()

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
    
