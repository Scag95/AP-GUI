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

        #2. Desplazamiento Máximo
        self.spin_drift = UnitSpinBox(UnitType.LENGTH)
        self.spin_drift.setRange(0,100)
        self.spin_drift.setDecimals(3)
        self.spin_drift.set_value_base(0.3) #Default 30cm

        form_layout.addRow("Nodo de Control (Techo):",self.combo_node)
        form_layout.addRow("Desplazamiento Máx:", self.spin_drift)

        layout.addLayout(form_layout)

        # --- BOTONES ---
        # Run Button
        self.btn_run = QPushButton("Ejecutar Pushover")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.btn_run.clicked.connect(self.run_pushover)
        layout.addWidget(self.btn_run)

        # --- GRAFICO ---
        um = UnitManager.instance()
        self.plot_widget = pg.PlotWidget(title = "Curva de capacidad (Pushover)")
        u_force = um.get_current_unit(UnitType.FORCE)
        u_len = um.get_current_unit(UnitType.LENGTH)
        self.plot_widget.setLabel('bottom', f"Desplazamiento Techo [{u_len}]")
        self.plot_widget.setLabel('left', f"Cortante Basal Vb [{u_force}]")
                
        self.plot_widget.getAxis('bottom').enableAutoSIPrefix(False)
        self.plot_widget.getAxis('left').enableAutoSIPrefix(False)

        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('w')

        self.curve_item = self.plot_widget.plot([],[],pen = pg.mkPen('b',width = 3))
        layout.addWidget(self.plot_widget)

    def populate_nodes(self):
        nodes = self.manager.get_all_nodes()
        if not nodes: return
        sorted_nodes = sorted(nodes, key = lambda n: n.y, reverse =True)

        for n in sorted_nodes:
            self.combo_node.addItem(f"Nodo {n.tag} (Y={n.y:.2f})", userData=n.tag)

    
    def run_pushover(self):
        from src.analysis.opensees_translator import OpenSeesTranslator
        um = UnitManager.instance()
        print(f"[DEBUG] UnitManager Length Unit: {um.get_current_unit(UnitType.LENGTH)}")
        #1. Obtenner inputs
        idx = self.combo_node.currentIndex()
        if idx < 0: return
        control_node = self.combo_node.itemData(idx)
        max_disp = self.spin_drift.get_value_base()

        #2. Instacniar Tranaltor y ejecutar
        translator = OpenSeesTranslator()

        print(f"Lanzando Pushover: Node {control_node}, Disp {max_disp}...")



        try: 
            #Ejecutar lógica backend
            dx, dy = translator.run_pushover_analysis(control_node, max_disp)
            len_unit = um.get_current_unit(UnitType.LENGTH)
            force_unit = um.get_current_unit(UnitType.FORCE)
            print(f"[DEBUG] Converting Results. Length Unit: {len_unit}, Force Unit: {force_unit}")
        
            vis_dx = [um.from_base(val, UnitType.LENGTH) for val in dx]
            print(f"[DEBUG] Conversion Check: Base {dx[-1]:.4f} -> Vis {vis_dx[-1]:.4f}")
            vis_dx = [um.from_base(val, UnitType.LENGTH) for val in dx]
            vis_dy = [um.from_base(val, UnitType.FORCE) for val in dy]
            if dx and dy:
                #3. Plotear Resultados
                self.curve_item.setData(vis_dx, vis_dy)
                print("Pushover finalizado con éxito")
            else:
                print("Pushover falló")

        except Exception as e:
            print(f"Error crítico en Pushover: {e}")
            import traceback
            traceback.print_exc()

