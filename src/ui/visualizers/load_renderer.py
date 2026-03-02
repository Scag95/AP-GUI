from PyQt6.QtCore import Qt
import pyqtgraph as pg
from src.analysis.loads import NodalLoad, ElementLoad
from src.utils.units import UnitType, UnitManager
import math

class LoadRenderer:
    def __init__(self):
        self.load_items = []
        # Colores estáticos
        self.color_nodal_load = '#FF5722'  # Naranja
        self.color_dist_load = '#9C27B0'   # Morado
        # Color dinámico
        self.color_pushover_load = '#00BCD4' # Cian

    def clear(self, plot_widget):
        """Elimina todos los items de carga del plot."""
        for item in self.load_items:
            plot_widget.removeItem(item)
        self.load_items.clear()

    def draw_loads(self, plot_widget, manager, scale=1.0, show_nodes=True, show_elements=True, draw_pushover=False):
        """Dibuja todas las cargas del manager en el plot_widget."""
        # Desactivamos actualizaciones para acelerar la inserción masiva de items
        plot_widget.setUpdatesEnabled(False)
        try:
            self.clear(plot_widget)

            # Pre-calc scales/constants
            um = UnitManager.instance()
            force_unit_str = um.get_current_unit(UnitType.FORCE)
            dist_unit_str = um.get_current_unit(UnitType.DISTRIBUTED_FORCE)
            
            # Use faster lookups
            if draw_pushover:
                all_loads = manager.pushover_loads
                color_override_nodal = self.color_pushover_load
                color_override_dist = self.color_pushover_load
            else:
                all_loads = manager.get_all_loads()
                color_override_nodal = self.color_nodal_load
                color_override_dist = self.color_dist_load
                
            nodes_map = {n.tag: n for n in manager.get_all_nodes()}
            elements_map = {e.tag: e for e in manager.get_all_elements()} # only needed if ElementLoads exist

            for load in all_loads:
                if isinstance(load, NodalLoad) and show_nodes:
                    node = nodes_map.get(load.node_tag)
                    if node:
                        self._draw_nodal_load(plot_widget, node, load, scale, um, force_unit_str, color_override=color_override_nodal, is_pushover=draw_pushover)
                
                elif isinstance(load, ElementLoad) and show_elements:
                    elem = elements_map.get(load.element_tag)
                    if elem:
                        ni = nodes_map.get(elem.node_i)
                        nj = nodes_map.get(elem.node_j)
                        if ni and nj:
                            self._draw_element_load(plot_widget, ni, nj, load, scale, um, dist_unit_str, color_override=color_override_dist)
        finally:
            plot_widget.setUpdatesEnabled(True)
            plot_widget.update()

    def _draw_nodal_load(self, plot_widget, node, load, scale, um, unit_str, color_override=None, is_pushover=False):
        # Parametros graficos
        HEAD_LEN = 1500 * scale
        OFFSET = 1000 * scale 
        TAIL_WIDTH = 0.1*scale
        color = color_override if color_override else 'g'
        # um passed as arg



        # FX
        if abs(load.fx) > 1e-6:
            # GEOMETRÍA: Usar valor BASE para que el tamaño sea constante al cambiar unidades
            # Si es pushover, la escala es muy chica (~1.0), le damos un empujón visual para que se vea junto a fuerzas reales
            base_val_x = abs(load.fx) * 10000 if is_pushover else abs(load.fx)
            tail_len = base_val_x * scale
            
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
                brush=color, pen=color, pxMode=False
            )
            plot_widget.addItem(item)
            self.load_items.append(item)
            
            # Texto (VISUAL: Usar conversiones)
            if is_pushover:
                val_viz = load.fx
                display_str = f"Fx={val_viz:.2f}"
            else:
                val_viz = um.from_base(load.fx, UnitType.FORCE)
                display_str = f"Fx={val_viz:.3f} {unit_str}"
                
            # Calculamos cola
            total_len = tail_len + HEAD_LEN
            shift_x = total_len if angle == 0 else -total_len
            
            text = pg.TextItem(display_str, color=color, anchor=(0.5, 1))
            text.setPos(node.x + shift_x, node.y)
            plot_widget.addItem(text)
            self.load_items.append(text)

        # FY
        if abs(load.fy) > 1e-6:
            # GEOMETRÍA: Valor BASE
            base_val_y = abs(load.fy) * 10000 if is_pushover else abs(load.fy)
            tail_len = base_val_y * scale
            angle = -90 if load.fy < 0 else 90 # Arriba(90) o Abajo(-90)
            color_y = color_override if color_override else '#FFA500'
            
            dy_offset = -OFFSET if angle == -90 else OFFSET
            tip_y = node.y + dy_offset

            item = pg.ArrowItem(
                pos=(node.x, tip_y),
                angle=angle,
                tipAngle=30, baseAngle=20, headLen=HEAD_LEN,
                tailLen=tail_len, tailWidth=TAIL_WIDTH,
                brush=color_y, pen=color_y, pxMode=False
            )
            plot_widget.addItem(item)
            self.load_items.append(item)
            
            # Texto (VISUAL)
            if is_pushover:
                val_viz = load.fy
                display_str = f"Fy={val_viz:.3f} (ref)"
            else:
                val_viz = um.from_base(load.fy, UnitType.FORCE)
                display_str = f"Fy={val_viz:.3f} {unit_str}"
                
            total_len = tail_len + HEAD_LEN
            dy = total_len if angle == 90 else -total_len
            
            text = pg.TextItem(display_str, color=color_y)
            text.setPos(node.x, node.y + dy)
            plot_widget.addItem(text)
            self.load_items.append(text)

    def _draw_element_load(self, plot_widget, ni, nj, load, scale, um, unit_str, color_override=None):
        # um passed as arg
        HEAD_LEN = 500 * scale
        OFFSET = 1000 * scale 
        dx = nj.x - ni.x
        dy = nj.y - ni.y
        length = math.sqrt(dx*dx + dy*dy)
        if length < 1e-9: return

        # Vectores unitarios (u: axial, n: normal)
        ux, uy = dx/length, dy/length
        nx, ny = -uy, ux 

        # Sub-funcion helper
        def draw_block(magnitude_base, color, is_axial):
            # magnitude_base: Valor en N/m (base)
            if abs(magnitude_base) < 1e-6: return

            direction = 1 if magnitude_base < 0 else -1
            
            # Geometría: Usar base para altura del bloque
            mag_geom = abs(magnitude_base) * scale*3
            
            off_x = nx * mag_geom * direction
            off_y = ny * mag_geom * direction
            
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
                    headLen=HEAD_LEN, tailLen=0,
                    brush=color, pen=None, pxMode=False
                )
                arrow.setStyle(angle=angle)
                plot_widget.addItem(arrow)
                self.load_items.append(arrow)
                
                # Palito
                conn = pg.PlotCurveItem([lx, bx], [ly, by], pen=pg.mkPen(color, width=1))
                plot_widget.addItem(conn)
                self.load_items.append(conn)
            
            # Label (VISUAL)
            mid_x = (p1_load[0] + p2_load[0]) / 2
            mid_y = (p1_load[1] + p2_load[1]) / 2
            
            text_offset = 500 * scale

            label_x = mid_x + nx * text_offset * direction
            label_y = mid_y + ny * text_offset * direction
            val_viz = um.from_base(magnitude_base, UnitType.DISTRIBUTED_FORCE)
            label = f"{'wx' if is_axial else 'wy'}={val_viz:.2f} {unit_str}"
            text = pg.TextItem(label, color=color, anchor=(0.5, 0.5)) # Anchor centrado
            text.setPos(label_x, label_y)
            plot_widget.addItem(text)
            self.load_items.append(text)

        # Llamadas: PASAMOS VALORES BASE SIN CONVERTIR
        draw_block(load.wy, color_override if color_override else self.color_nodal_load, False) 
        draw_block(load.wx, color_override if color_override else self.color_dist_load, True)
