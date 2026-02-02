import pyqtgraph as pg
from src.analysis.manager import ProjectManager
from src.utils.units import UnitManager, UnitType
from src.utils.scale_manager import ScaleManager
import math

from PyQt6.QtWidgets import QGraphicsPolygonItem
from PyQt6.QtGui import QPolygonF, QColor, QPen, QBrush
from PyQt6.QtCore import QPointF

class ForceDiagramRenderer:
    def __init__(self):
        self.diagram_items = []
         # Colores: Momento(Rojo/Azul), Cortante(Verde), Axial(Naranja)

    def clear(self, plot_widget):
        for item in self.diagram_items:
            plot_widget.removeItem(item)
        self.diagram_items.clear()

    def draw_diagrams(self, plot_widget, manager, element_forces, type='M'):
        self.clear(plot_widget)

        lobatto_locs = [0.0, 0.17267, 0.5, 0.82733, 1.0]

        # 1. Obtener escala del singleton
        scale_key = 'moment'
        if type == 'V': scale_key = 'shear'
        elif type == 'P': scale_key = 'axial'

        scale_factor = ScaleManager.instance().get_scale(scale_key)
        for ele in manager.get_all_elements():
            if ele.tag not in element_forces: continue

            sections_data = element_forces[ele.tag]
            


            #Extraer la seire de valores a dibujar

            values = []
            u_type = UnitType.FORCE  # Por defecto Fuerza
            color = '#FFFFFF'

            # Extraer valores según 'type'
            if type == 'M':
                color = '#FF5252' # Rojo (Momentos)
                u_type = UnitType.MOMENT
                values = [s['M'] for s in sections_data]
            elif type == 'V':
                color = '#4CAF50' # Verde (Cortante)
                u_type = UnitType.FORCE
                values = [s['V'] for s in sections_data]
            elif type == 'P':
                color = '#FF9800' # Naranja (Axial)
                u_type = UnitType.FORCE
                values = [s['P'] for s in sections_data]
            else:
                continue

            self._draw_element_diagram_detailed(plot_widget, ele, values, lobatto_locs, scale_factor, color, u_type)

    def _draw_element_diagram_detailed(self, plot_widget, ele, values, locs, scale, color, u_type):
        # 1. Obtener coordenadas
        manager = ProjectManager.instance()
        ni = manager.get_node(ele.node_i)
        nj = manager.get_node(ele.node_j)

        if not ni or not nj: return

        # 2. Geometría base
        dx = nj.x - ni.x
        dy = nj.y - ni.y
        L = math.sqrt(dx**2 + dy**2)
        if L < 1e-9: return

        ux, uy = dx/L, dy/L
        nx, ny = -uy, ux  

        # 3. Conversión de Unidades
        um = UnitManager.instance()
        
        # Construir polígono
        # Empezamos en el nodo I
        polygon_x = [ni.x]
        polygon_y = [ni.y]
        # Recorremos los puntos de integración
        # Asumimos que len(values) == len(locs) == 5
        count = min(len(values), len(locs))
        
        for k in range(count):
            val_base = values[k]
            rel_pos = locs[k] # 0.0 a 1.0
            
            # Conversión unitaria
            val_viz = um.from_base(val_base, u_type)
            
            # Calcular posición en el eje de la viga
            base_x = ni.x + ux * (L * rel_pos)
            base_y = ni.y + uy * (L * rel_pos)
            
            offset = val_viz * scale 
            
            px = base_x + nx * offset
            py = base_y + ny * offset
            
            polygon_x.append(px)
            polygon_y.append(py)

        # Terminamos en nodo J (volver al eje)
        polygon_x.append(nj.x)
        polygon_y.append(nj.y)
        
        # Cerrar en nodo I
        polygon_x.append(ni.x)
        polygon_y.append(ni.y)

        # 4. Crear Item (Polígono Real)
        poly = QPolygonF()
        for x, y in zip(polygon_x, polygon_y):
            poly.append(QPointF(x, y))
            
        item = QGraphicsPolygonItem(poly)
        
        # Configurar Borde
        border_color = QColor(color)
        pen = QPen(border_color)
        pen.setWidthF(2) # setWidthF permite grosores no enteros si quisieras, width es int
        pen.setCosmetic(True) # Mantiene grosor al hacer zoom (opcional, visualmente mejor)
        item.setPen(pen)
        
        # Configurar Relleno
        fill_color = QColor(color)
        fill_color.setAlpha(64) # '40' hex aprox 64 int
        brush = QBrush(fill_color)
        item.setBrush(brush)
        
        item.setZValue(20)
        plot_widget.addItem(item)
        self.diagram_items.append(item)

