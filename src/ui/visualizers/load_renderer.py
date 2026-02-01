from PyQt6.QtCore import Qt
import pyqtgraph as pg
from src.analysis.loads import NodalLoad, ElementLoad
from src.utils.units import UnitType, UnitManager
import math

class LoadRenderer:
    def __init__(self):
        self.load_items = []
        # Colores
        self.color_nodal_load = '#FF5722'  # Naranja
        self.color_dist_load = '#9C27B0'   # Morado

    def clear(self, plot_widget):
        """Elimina todos los items de carga del plot."""
        for item in self.load_items:
            plot_widget.removeItem(item)
        self.load_items.clear()

    def draw_loads(self, plot_widget, manager, scale=1.0):
        """Dibuja todas las cargas del manager en el plot_widget."""
        self.clear(plot_widget)

        loads = manager.get_all_loads()
        valid_nodes = {n.tag: n for n in manager.get_all_nodes()}
        valid_elements = {e.tag: e for e in manager.get_all_elements()}

        for load in loads:
            if isinstance(load, NodalLoad):
                if load.node_tag in valid_nodes:
                    node = valid_nodes[load.node_tag]
                    self._draw_nodal_load(plot_widget, node, load, scale)
            
            elif isinstance(load, ElementLoad):
                if load.element_tag in valid_elements:
                    elem = valid_elements[load.element_tag]
                    if elem.node_i in valid_nodes and elem.node_j in valid_nodes:
                        ni = valid_nodes[elem.node_i]
                        nj = valid_nodes[elem.node_j]
                        self._draw_element_load(plot_widget, ni, nj, load, scale)

    def _draw_nodal_load(self, plot_widget, node, load, scale):
        # Parametros graficos
        HEAD_LEN = 2 * scale
        OFFSET = 2.0 * scale 
        TAIL_WIDTH = 0.1*scale
        um = UnitManager.instance()


        # FX
        if abs(load.fx) > 1e-6:
            tail_len = abs(um.from_base(load.fx,UnitType.FORCE)) * scale
            
            # Ángulo de la flecha
            angle = 180 if load.fx > 0 else 0
            
            # Offset del punto de insercion (la punta)
            dx_offset = -OFFSET if angle == 180 else OFFSET
            tip_x = node.x + dx_offset
            
            item = pg.ArrowItem(
                pos=(tip_x, node.y),
                angle=angle,
                tipAngle=30, baseAngle=20, headLen=HEAD_LEN,
                tailLen=tail_len, tailWidth=TAIL_WIDTH,
                brush='g', pen='g', pxMode=False
            )
            plot_widget.addItem(item)
            self.load_items.append(item)
            
            # Texto
            # Calculamos cola
            total_len = tail_len + HEAD_LEN
            shift_x = total_len if angle == 0 else -total_len
            
            text = pg.TextItem(f"Fx={um.from_base(load.fx,UnitType.FORCE):.1f} {um.get_current_unit(UnitType.FORCE)}", color='g', anchor=(0.5, 1))
            text.setPos(node.x + shift_x, node.y)
            plot_widget.addItem(text)
            self.load_items.append(text)

        # FY
        if abs(load.fy) > 1e-6:
            tail_len = abs(abs(um.from_base(load.fy,UnitType.FORCE))) * scale
            angle = -90 if load.fy < 0 else 90 # Arriba(90) o Abajo(-90)
            
            dy_offset = -OFFSET if angle == -90 else OFFSET
            tip_y = node.y + dy_offset

            item = pg.ArrowItem(
                pos=(node.x, tip_y),
                angle=angle,
                tipAngle=30, baseAngle=20, headLen=HEAD_LEN,
                tailLen=tail_len, tailWidth=TAIL_WIDTH,
                brush='#FFA500', pen='#FFA500', pxMode=False
            )
            plot_widget.addItem(item)
            self.load_items.append(item)
            
            # Texto
            total_len = tail_len + HEAD_LEN
            dy = total_len if angle == 90 else -total_len
            
            text = pg.TextItem(f"Fy={um.from_base(load.fy,UnitType.FORCE):.1f} {um.get_current_unit(UnitType.FORCE)}", color='#FFA500')
            text.setPos(node.x, node.y + dy)
            plot_widget.addItem(text)
            self.load_items.append(text)

    def _draw_element_load(self, plot_widget, ni, nj, load, scale):
        um = UnitManager.instance()

        dx = nj.x - ni.x
        dy = nj.y - ni.y
        length = math.sqrt(dx*dx + dy*dy)
        if length < 1e-9: return

        # Vectores unitarios (u: axial, n: normal)
        ux, uy = dx/length, dy/length
        nx, ny = -uy, ux 

        # Sub-funcion helper
        def draw_block(magnitude, color, is_axial):
            if abs(magnitude) < 1e-6: return

            direction = 1 if magnitude < 0 else -1
            mag_visual = abs(magnitude) * scale
            
            off_x = nx * mag_visual * direction
            off_y = ny * mag_visual * direction
            
            x1, y1 = ni.x, ni.y
            x2, y2 = nj.x, nj.y
            p1_load = (x1 + off_x, y1 + off_y)
            p2_load = (x2 + off_x, y2 + off_y)

            # Techo
            curve = pg.PlotCurveItem(
                [p1_load[0], p2_load[0]], 
                [p1_load[1], p2_load[1]], 
                pen=pg.mkPen(color, width=1)
            )
            plot_widget.addItem(curve)
            self.load_items.append(curve)
            
            # Flechas internas (3)
            import numpy as np
            NUM_ARROWS = 3 
            for i in range(NUM_ARROWS + 1):
                t = i / NUM_ARROWS
                bx = x1 + dx * t
                by = y1 + dy * t
                lx = p1_load[0] + (p2_load[0] - p1_load[0]) * t 
                ly = p1_load[1] + (p2_load[1] - p1_load[1]) * t

                # Vector flecha: Techo -> Viga
                ax, ay = bx - lx, by - ly
                angle = np.degrees(np.arctan2(ay, ax)) + 180
                
                arrow = pg.ArrowItem(
                    pos=(bx, by),
                    headLen=3 * scale, tailLen=0,
                    brush=color, pen=None, pxMode=False
                )
                arrow.setStyle(angle=angle)
                plot_widget.addItem(arrow)
                self.load_items.append(arrow)
                
                # Palito
                conn = pg.PlotCurveItem([lx, bx], [ly, by], pen=pg.mkPen(color, width=1))
                plot_widget.addItem(conn)
                self.load_items.append(conn)
            
            # Label
            mid_x = (p1_load[0] + p2_load[0]) / 2
            mid_y = (p1_load[1] + p2_load[1]) / 2
            label = f"{'wx' if is_axial else 'wy'}={magnitude:.2f} {um.get_current_unit(UnitType.DISTRIBUTED_FORCE)}"
            text = pg.TextItem(label, color=color, anchor=(0.5, 0))
            text.setPos(mid_x, mid_y)
            plot_widget.addItem(text)
            self.load_items.append(text)

        # Llamadas
        draw_block(um.from_base(load.wy,UnitType.DISTRIBUTED_FORCE), self.color_nodal_load, False) # Wy usa color naranja/rojo
        draw_block(um.from_base(load.wx,UnitType.DISTRIBUTED_FORCE), self.color_dist_load, True)   # Wx usa color morado
