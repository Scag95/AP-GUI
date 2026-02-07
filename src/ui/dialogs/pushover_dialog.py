import pyqtgraph as pg
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QComboBox, QPushButton, QLabel, QDialogButtonBox)
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
        self.combo_load_pattern_type.addItems(["Modal","Unitario"])


        #2. Desplazamiento Máximo
        self.spin_drift = UnitSpinBox(UnitType.LENGTH)
        self.spin_drift.setRange(0,100)
        self.spin_drift.setDecimals(3)
        self.spin_drift.set_value_base(0.3) #Default 30cm

        form_layout.addRow("Nodo de Control:",self.combo_node)
        form_layout.addRow("Desplazamiento Máx:", self.spin_drift)
        form_layout.addRow("Modo de aplicación de fuerza", self.combo_load_pattern_type)
        
        layout.addLayout(form_layout)

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


        #2. Instacniar Tranaltor y ejecutar
        translator = OpenSeesTranslator()

        print(f"Lanzando Pushover: Node {control_node}, Disp {max_disp}, Pattern {load_pattern_type}")



        try: 
            #Ejecutar lógica backend
            results = translator.run_pushover_analysis(control_node, max_disp, load_pattern_type)
            if results:
                # Pasamos el diccionario crudo al dialog de resultados
                # Dejamos que ResultsDialog gestione las unidades internamente
                from src.ui.dialogs.pushover_result_dialog import PushoverResultsDialog
                dlg = PushoverResultsDialog(results, self)
                dlg.exec()

        except Exception as e:
            print(f"Error crítico en Pushover: {e}")
            import traceback
            traceback.print_exc()

