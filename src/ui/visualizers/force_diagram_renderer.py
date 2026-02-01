import pyqtgraph as pg
from src.analysis.manager import ProjectManager
from src.utils.units import UnitManager, UnitType
import math

class ForceDiagramRenderer:
    def __init__(self):
        self.diagram_items = []
         # Colores: Momento(Rojo/Azul), Cortante(Verde), Axial(Naranja)

    def clear(self, plot_widget):
        for item in self.diagram_items:
            plot_widget.removeItem(item)
        self.diagram_items.clear()

    def draw_diagrams(self, plot_widget, manager, element_forces, type='M', scale_factor=1.0):
        self.clear(plot_widget)
        for ele in manager.get_all_elements():
            if ele.tag not in element_forces: continue

            forces = element_forces[ele.tag]
            
            # Default values
            val_i, val_j = 0, 0
            u_type = UnitType.FORCE  # Por defecto Fuerza
            
            # Extraer valores según 'type'
            if type == 'M':
                color = '#FF5252' # Rojo (Momentos)
                u_type = UnitType.MOMENT
                # Momentos en extremos (indices 2 y 5) [Fx, Fy, Mz, Fx, Fy, Mz]
                val_i, val_j = forces[2], forces[5]

            elif type == 'V':
                color = '#4CAF50' # Verde (Cortante)
                u_type = UnitType.FORCE
                # Cortante (indices 1 y 4)
                val_i, val_j = forces[1], forces[4]
            
            elif type == 'P':
                color = '#FF9800' # Naranja (Axial)
                u_type = UnitType.FORCE
                # Axial (indices 0 y 3)
                val_i, val_j = forces[0], forces[3]
            
            else:
                continue

            self._draw_element_diagram(plot_widget, ele, val_i, val_j, scale_factor, color, u_type)

    def _draw_element_diagram(self, plot_widget, ele, val_i, val_j, scale, color, u_type):
        #1. Obtener coordenadas
        manager = ProjectManager.instance()
        ni = manager.get_node(ele.node_i)
        nj = manager.get_node(ele.node_j)

        if not ni or not nj: return

        #2. vector dirección
        dx = nj.x-ni.x
        dy = nj.y-ni.y
        L = math.sqrt(dx**2+dy**2)
        if L<1e-9: return 

        ux, uy = dx/L, dy/L
        nx, ny = -uy, ux  

        # 3. Conversión de Unidades
        um = UnitManager.instance()
        
        # Convertimos de Base -> Visual. E.g. 10000 N -> 10 kN
        # Esto reduce drásticamente la magnitud numérica
        visual_val_i = um.from_base(val_i, u_type)
        visual_val_j = um.from_base(val_j, u_type)

        # 4. Calcular puntos desplazados (Diagrama)
        # OJO: OpenSees da fuerzas en extremos.
        # Ajustaremos signos visualmente ahora.

        vis_val_i = visual_val_i * scale
        vis_val_j = -visual_val_j * scale

        #Puntos del polígono (4 vértices)

        #Offset I
        xi_off = ni.x + nx * vis_val_i
        yi_off = ni.y + ny * vis_val_i
        
        #Offset J
        xj_off = nj.x + nx * vis_val_j
        yj_off = nj.y + ny * vis_val_j

        x_poly = [ni.x, xi_off, xj_off, nj.x, ni.x] 
        y_poly = [ni.y, yi_off, yj_off, nj.y, ni.y]
        print(f"Ele {ele.tag} Forces: I={val_i:.2f}, J={val_j:.2f}")
        # 4. Crear Item
        item = pg.PlotCurveItem(
            x_poly, y_poly,
            pen=pg.mkPen(color, width=2),
            brush=pg.mkBrush(color = color + '40'),
            fillLevel= None
        )
        item.setZValue(20)
        plot_widget.addItem(item)
        self.diagram_items.append(item)

