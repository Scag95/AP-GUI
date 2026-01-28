import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from src.analysis.manager import ProjectManager
from src.analysis.loads import NodalLoad, ElementLoad

class StructureInteractor(QWidget):
    nodeSelected = pyqtSignal(object)
    selectionCleared = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        #Configurar el lienzo gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=False,y=False, alpha=0.3)
        self.plot_widget.setAspectLocked(True)


        self.layout.addWidget(self.plot_widget)
        self.manager = ProjectManager.instance()
        self.manager.dataChanged.connect(self.refresh_viz)
        self.last_clicked_point = None
        self.current_label = None
        self.plot_widget.scene().sigMouseClicked.connect(self._on_background_clicked)

    def refresh_viz(self):
        self.last_clicked_point = None
        self.current_label = None 
        self.plot_widget.clear()

        #1. Dibujar Elementos (Lineas)
        elements = self.manager.get_all_elements()

        for ele in elements:
            node_i = self.manager.get_node(ele.node_i)
            node_j = self.manager.get_node(ele.node_j)

            if node_i and node_j:
                #dibujar lineas neagras entre nodos
                self.plot_widget.plot(
                    [node_i.x, node_j.x],
                    [node_i.y, node_j.y],
                    pen=pg.mkPen('k',width=2)
                )
        #2. dibujar nodos(Puntos azules)
        nodes = self.manager.get_all_nodes()
        if nodes:
            x_vals=[n.x for n in nodes]
            y_vals=[n.y for n in nodes]
            data_vals = nodes

            scatter= pg.ScatterPlotItem(
                x=x_vals,
                y=y_vals,
                data=data_vals,
                size=8,
                brush=pg.mkBrush('b'),
                pxMode=True,
                hoverable = True
            )
            scatter.sigClicked.connect(self._on_node_clicked)
            self.plot_widget.addItem(scatter)
        #3. dibujar Cargas
        self._draw_loads()
        print("[DEBUG] Visualización actualizada.")

    def _on_node_clicked(self, plot_item, points):
        self._deselect_all()

        # 2. Procesar el nuevo punto seleccionado
        if points:
            p = points[0] # Tomamos el primer punto detectado
            p.setBrush('r') # Lo pintamos de ROJO
            self.last_clicked_point = p # Guardamos referencia
            
            node = p.data()
            self.nodeSelected.emit(node)
            print(f"Seleccionado Nodo {node.tag} (x={node.x}, y={node.y})")

            text_item = pg.TextItem(
                text = f"ID: {node.tag}",
                color = 'k',
                anchor = (0,0)
            )
            text_item.setPos(node.x, node.y)

            self.plot_widget.addItem(text_item)
            self.current_label = text_item

    def _deselect_all(self):
        if self.last_clicked_point is not None:
            self.last_clicked_point.resetBrush()
            self.last_clicked_point = None
            
        if self.current_label is not None:
            self.plot_widget.removeItem(self.current_label)
            self.current_label = None

        self.selectionCleared.emit()
    

    def _on_background_clicked(self, event):
        # Obtenemos la posición del click en la escena
        pos = event.scenePos()
        
        # Verificamos si hay scatter points debajo
        items = self.plot_widget.scene().items(pos)
        hit_node = any(isinstance(x, pg.ScatterPlotItem) for x in items)
        
        if not hit_node:
            self._deselect_all()

    def _draw_loads(self):
        loads = self.manager.get_all_loads()
        for load in loads:
            if isinstance(load, NodalLoad):
                self._draw_nodal_load(load)

    def _draw_nodal_load(self,load):
        node = self.manager.get_node(load.node_tag)
        if not node:
            return
        
        SCALE = 0.05
        HEAD_LEN = 5 * SCALE
        OFFSET = 2.0 * SCALE 

        # --- Cargas Horizontales (Fx) ---
        if abs(load.fx) > 1e-6:
            tail_len = abs(load.fx) * SCALE
            angle = 180 if load.fx > 0 else 0   
            dx_offset = -OFFSET if angle == 180 else OFFSET  
            tip_x = node.x + dx_offset
            tip_y = node.y
            arrow = pg.ArrowItem(
                pos=(tip_x, tip_y),
                angle=angle,
                tipAngle=30,
                baseAngle=20,
                headLen=HEAD_LEN,
                tailLen=tail_len,
                brush='g',
                tailWidth=0.1 * SCALE,
                pen='g',
                pxMode=False
            )
            self.plot_widget.addItem(arrow)

            # Calcular la posición exacta del final de la cola
            total_len = tail_len + HEAD_LEN      
            
            # Invertir lógica: Si el usuario dice que sale al revés, probamos el otro lado.
            shift_x = total_len if angle == 0 else -total_len
            
            tail_x = node.x + shift_x
            tail_y = node.y
            
            # Texto "Fx=..." justo encima de la cola
            text = pg.TextItem(f"Fx={load.fx:.1f}", color='g', anchor=(0.5, 1)) 
            text.setPos(tail_x, tail_y)
            self.plot_widget.addItem(text)

        # --- Cargas Verticales (Fy) ---
        if abs(load.fy) > 1e-6:
            tail_len = abs(load.fy) * SCALE
            angle = -90 if load.fy < 0 else 90
            dy_offset = -OFFSET if angle == -90 else OFFSET
            tip_x = node.x
            tip_y = node.y + dy_offset
            arrow = pg.ArrowItem(
                pos=(tip_x, tip_y),
                angle=angle,
                tipAngle=30,
                baseAngle=20,
                headLen=HEAD_LEN,
                tailWidth =0.1*SCALE,
                tailLen=tail_len,
                brush='#FFA500', 
                pen='#FFA500',
                pxMode=False
            )
            self.plot_widget.addItem(arrow)

            total_len = tail_len + HEAD_LEN
            dy = total_len if angle == 90 else -total_len
            
            tail_x = node.x
            tail_y = node.y + dy
            
            text = pg.TextItem(f"Fy={load.fy:.1f}", color='#FFA500')
            text.setPos(tail_x, tail_y)
            
            self.plot_widget.addItem(text)