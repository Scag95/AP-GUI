import pyqtgraph as pg
from src.analysis.manager import ProjectManager
from src.utils.units import UnitManager, UnitType
from src.utils.scale_manager import ScaleManager
import math

from PyQt6.QtWidgets import QGraphicsPolygonItem
from PyQt6.QtGui import QPolygonF, QColor, QPen, QBrush, QFont 
from PyQt6.QtCore import QPointF, QRectF

class MassivePolygonsItem(pg.GraphicsObject):
    """
    Objeto gráfico de altísimo rendimiento que dibuja miles de polígonos
    en una sola pasada (paint) sin depender del árbol de Qt.
    Evita las cancelaciones de WindingRule entre formas opuestas.
    """
    def __init__(self, polygons, pen, brush):
        super().__init__()
        self.polygons = polygons
        self.my_pen = pen
        self.my_brush = brush
        
        self._bounds = QRectF()
        if polygons:
            # Calcular Caja delimitadora master para el renderizado
            self._bounds = polygons[0].boundingRect()
            for p in polygons[1:]:
                self._bounds = self._bounds.united(p.boundingRect())
                
    def boundingRect(self):
        return self._bounds
        
    def paint(self, painter, *args):
        # 1 Invocación directa a la tarjeta gráfica con estilo común
        painter.setPen(self.my_pen)
        painter.setBrush(self.my_brush)
        for poly in self.polygons:
            painter.drawPolygon(poly)


class ForceDiagramRenderer:
    def __init__(self):
        self.diagram_items = []

    def clear(self, plot_widget):
        for item in self.diagram_items:
            plot_widget.removeItem(item)
        self.diagram_items.clear()

    def draw_diagrams(self, plot_widget, manager, element_forces, type='M'):
        self.clear(plot_widget)

        # 1. Obtener escala del singleton
        scale_key = 'moment'
        if type == 'V': scale_key = 'shear'
        elif type == 'P': scale_key = 'axial'

        scale_factor = ScaleManager.instance().get_scale(scale_key)
        
        # 2. Configurar colores y tipo de unidad globales para este renderizado
        color = '#FFFFFF'
        u_type = UnitType.FORCE
        if type == 'M':
            color = '#FF5252' # Rojo (Momentos)
            u_type = UnitType.MOMENT
        elif type == 'V':
            color = '#4CAF50' # Verde (Cortante)
            u_type = UnitType.FORCE
        elif type == 'P':
            color = '#FF9800' # Naranja (Axial)
            u_type = UnitType.FORCE
        else:
            return

        polygons_buffer = []

        for ele in manager.get_all_elements():
            if ele.tag not in element_forces: continue

            sections_data = element_forces[ele.tag]
            lobatto_locs = [s['loc'] for s in sections_data]
            
            # Extraer valores numéricos
            values = []
            if type == 'M':
                values = [-1*s['M'] for s in sections_data]
            elif type == 'V':
                values = [s['V'] for s in sections_data]
            elif type == 'P':
                values = [s['P'] for s in sections_data]

            self._draw_element_diagram_detailed(plot_widget, ele, values, lobatto_locs, scale_factor, color, u_type, polygons_buffer)

        # 3. Dibujar TODOS los polígonos del modelo de una sola vez sumados linealmente
        if polygons_buffer:
            # Configurar Borde Unificado
            border_color = QColor(color)
            pen = QPen(border_color)
            pen.setWidthF(2) 
            pen.setCosmetic(True) 
            
            # Configurar Relleno Unificado
            fill_color = QColor(color)
            fill_color.setAlpha(64) 
            brush = QBrush(fill_color)
            
            master_item = MassivePolygonsItem(polygons_buffer, pen, brush)
            master_item.setZValue(20)
            plot_widget.addItem(master_item)
            self.diagram_items.append(master_item)

    def _draw_element_diagram_detailed(self, plot_widget, ele, values, locs, scale, color, u_type, polygons_buffer):
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

        # 3. Conversión de Unidades y Vértices matemáticos
        um = UnitManager.instance()
        polygon_x = [ni.x]
        polygon_y = [ni.y]
        
        count = min(len(values), len(locs))
        for k in range(count):
            val_base = values[k]
            val_viz = um.from_base(val_base, u_type)
            
            base_x = ni.x + ux * locs[k]
            base_y = ni.y + uy * locs[k]
            
            offset = val_viz * scale 
            
            px = base_x + nx * offset
            py = base_y + ny * offset
            
            polygon_x.append(px)
            polygon_y.append(py)

        # Terminamos en nodo J y cerramos el polígono
        polygon_x.append(nj.x)
        polygon_y.append(nj.y)
        polygon_x.append(ni.x)
        polygon_y.append(ni.y)

        # 4. Almacenamos polígono validado en el buffer maestro
        poly = QPolygonF()
        for x, y in zip(polygon_x, polygon_y):
            poly.append(QPointF(x, y))
            
        polygons_buffer.append(poly)

        # 5. Visualizar Textos (Extremos) independientemente
        if not values: return
        
        indices_to_label = [0, len(values)-1]
        for idx in indices_to_label:
            val_base = values[idx]
            if abs(val_base) < 1e-6:
                continue
                
            val_viz = um.from_base(val_base, u_type)
            text_str = f"{val_viz:.2f}" 
            
            base_x = ni.x + ux * locs[idx]
            base_y = ni.y + uy * locs[idx]
            
            offset_viz = val_viz * scale 
            margin_factor = 1.15 
            
            px = base_x + nx * (offset_viz * margin_factor)
            py = base_y + ny * (offset_viz * margin_factor)
            
            text_item = pg.TextItem(text=text_str, color=color, anchor=(0.5, 0.5))
            text_item.setPos(px, py)
            
            font = QFont()
            font.setPixelSize(12) 
            text_item.setFont(font)
            text_item.setZValue(25)
            plot_widget.addItem(text_item)
            self.diagram_items.append(text_item)