import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
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

        # View Options
        self.show_node_labels = False 
        self.show_element_labels = False
        
        # --- ATRIBUTO DE ESCALA ---
        self.load_scale = 0.05 # Valor por defecto (antes era SCALE local)
        # --- ATAJOS DE TECLADO ---
        # Ctrl + '+' para aumentar
        self.shortcut_inc = QShortcut(QKeySequence("Ctrl++"), self)
        self.shortcut_inc.activated.connect(self.increase_load_scale)
        # Ctrl + '-' para disminuir
        self.shortcut_dec = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_dec.activated.connect(self.decrease_load_scale)


        self.plot_widget.scene().sigMouseClicked.connect(self._on_background_clicked)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "overlay_widget") and self.overlay_widget:
            w = self.width()
            # Usamos la altura actual del widget
            h_overlay = self.overlay_widget.height() 
            h_parent = self.height()
            
            # Lo colocamos pegado abajo
            self.overlay_widget.setGeometry(0, h_parent - h_overlay, w, h_overlay)


    def set_overlay_widget(self, widget):
        self.overlay_widget = widget
        widget.setParent(self)
        widget.show()
        
        # Inicializar tamaño
        # widget.setFixedHeight(40) # Ya lo hace el propio widget
        self.resizeEvent(None)

    def increase_load_scale(self):
        self.load_scale *= 1.2 # Aumentar un 20%
        print(f"[DEBUG] Escala aumentada a: {self.load_scale:.4f}")
        self.refresh_viz()

    def decrease_load_scale(self):
        self.load_scale /= 1.2 # Reducir
        print(f"[DEBUG] Escala reducida a: {self.load_scale:.4f}")
        self.refresh_viz()



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

        #4. Etiquetas (Labels)
        if self.show_node_labels:
            self._draw_node_labels()
        
        if self.show_element_labels:
            self._draw_element_labels()

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
            elif isinstance(load, ElementLoad):  
                self._draw_element_load(load)

    def _draw_nodal_load(self,load):
        node = self.manager.get_node(load.node_tag)
        if not node:
            return
        
        SCALE = self.load_scale
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
                tailWidth=0.3 * SCALE,
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
                tailWidth =0.3*SCALE,
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

    def toggle_node_labels(self, visible: bool):
        self.show_node_labels = visible
        self.refresh_viz()

    def toggle_element_labels(self, visible: bool):
        self.show_element_labels = visible
        self.refresh_viz()

    def _draw_node_labels(self):
        nodes = self.manager.get_all_nodes()
        for node in nodes:
            tag_html = f'<div style="color: blue; font-weight: bold; background-color: rgba(255,255,255,0.8); padding: 2px;">{node.tag}</div>'
            text = pg.TextItem(html=tag_html, anchor=(1, 1))
            text.setPos(node.x, node.y)
            text.setZValue(100) # Forzar que esté MUY por encima de líneas (Z=0) y nodos (Z=10)
            self.plot_widget.addItem(text)

    def _draw_element_labels(self):
        elements = self.manager.get_all_elements()
        for ele in elements:
            # Calcular centro del elemento
            ni = self.manager.get_node(ele.node_i)
            nj = self.manager.get_node(ele.node_j)
            if ni and nj:
                mid_x = (ni.x + nj.x) / 2
                mid_y = (ni.y + nj.y) / 2
                
                text = pg.TextItem(f"[{ele.tag}]", color='k', anchor=(1, 1))
                # Fondo blanco semitransparente para que se lea mejor sobre la línea
                text.setHtml(f'<div style="background-color: rgba(255, 255, 255, 0.7);">{ele.tag}</div>')
                text.setPos(mid_x, mid_y)
                self.plot_widget.addItem(text)

    def _draw_element_load(self, load):
        """Dibuja cargas distribuidas (rectángulos con flechas) sobre los elementos."""
        element = self.manager.get_element(load.element_tag)
        if not element: return
        
        ni = self.manager.get_node(element.node_i)
        nj = self.manager.get_node(element.node_j)
        if not ni or not nj: return

        # --- Geometría Base ---
        x1, y1 = ni.x, ni.y
        x2, y2 = nj.x, nj.y
        dx, dy = x2 - x1, y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        if length < 1e-9: return

        # Vectores unitarios (u: axial, n: normal)
        ux, uy = dx/length, dy/length
        nx, ny = -uy, ux # Normal perpendicular izquierda
        
        SCALE = self.load_scale 

        # --- Helper para dibujar bloques de carga ---
        def draw_load_block(magnitude, color, is_axial=False):
            if abs(magnitude) < 1e-6: return

            # Dirección del desplazamiento visual (techo de la carga)
            # Wy: Si es negativo (<0), dibujamos hacia arriba (normal +) para indicar presión hacia abajo?
            # Ajustamos para evitar solapamientos.
            direction = 1 if magnitude < 0 else -1
            
            # Magnitud gráfica
            mag_visual = abs(magnitude) * SCALE
            
            # Vector desplazamiento
            off_x = nx * mag_visual * direction
            off_y = ny * mag_visual * direction
            
            # Coordenadas del "Techo" de la carga
            p1_load = (x1 + off_x, y1 + off_y)
            p2_load = (x2 + off_x, y2 + off_y)

            # 1. Dibujar línea del techo
            self.plot_widget.plot(
                [p1_load[0], p2_load[0]], 
                [p1_load[1], p2_load[1]], 
                pen=pg.mkPen(color, width=1)
            )

            # 2. Dibujar flechas internas (conectando Techo -> Viga)
            NUM_ARROWS = 3 
            for i in range(NUM_ARROWS + 1):
                t = i / NUM_ARROWS
                
                # Puntos interpolados
                bx = x1 + dx * t  # En la viga
                by = y1 + dy * t
                lx = p1_load[0] + (p2_load[0] - p1_load[0]) * t # En el techo
                ly = p1_load[1] + (p2_load[1] - p1_load[1]) * t

                # Vector dirección de la flecha: DEL TECHO A LA VIGA
                ax, ay = bx - lx, by - ly
                angle = np.degrees(np.arctan2(ay, ax))+180
                
                # Ajuste rotación ArrowItem (0º es derecha)
                # Si el sistema rota mal, sumamos 180.
                # Con pxMode=False, el tamaño escala con el zoom.
                arrow = pg.ArrowItem(
                    pos=(bx, by), # Punta tocando la viga
                    headLen=5 * SCALE,
                    tailLen=0,
                    brush=color, pen=None,
                    pxMode=False
                )
                arrow.setStyle(angle=angle) 
                self.plot_widget.addItem(arrow)

                # Línea conectora (palito)
                self.plot_widget.plot([lx, bx], [ly, by], pen=pg.mkPen(color, width=1))

            # 3. Texto de magnitud
            mid_x = (p1_load[0] + p2_load[0]) / 2
            mid_y = (p1_load[1] + p2_load[1]) / 2
            label = f"{'wx' if is_axial else 'wy'}={magnitude:.2f}"
            text = pg.TextItem(label, color=color, anchor=(0.5, 0))
            text.setPos(mid_x, mid_y)
            self.plot_widget.addItem(text)

        # --- Dibujar Wy (Transversal - Naranja) ---
        draw_load_block(load.wy, '#FF5722', is_axial=False)

        # --- Dibujar Wx (Axial - Morado) ---
        draw_load_block(load.wx, '#9C27B0', is_axial=True)