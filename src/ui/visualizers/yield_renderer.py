import pyqtgraph as pg
from src.utils.scale_manager import ScaleManager


class YieldRenderer:

    def __init__(self):
        self.yield_scatter = pg.ScatterPlotItem(pxMode=True)
        self.yield_scatter.setZValue(200)
        self._in_scene = False

    def clear(self, plot_widget):
        if self._in_scene:
            plot_widget.removeItem(self.yield_scatter)
            self._in_scene = False

    def draw_yield_state(self, plot_widget, manager, step_yield_data, step_displacements):
        """
        Pinta un punto por sección fluida sobre la forma deformada.
        step_yield_data:    { ele_tag: { sec_num: { ratio, strain, loc } } }
        step_displacements: { node_tag: [dx, dy, rz] }
        """
        self.clear(plot_widget)

        if not step_yield_data:
            return

        scale_factor = ScaleManager.instance().get_scale('deformation')
        node_map     = {n.tag: n for n in manager.get_all_nodes()}
        spots        = []

        for ele_tag, sections in step_yield_data.items():
            ele = manager.get_element(ele_tag)
            if ele is None:
                continue

            ni = node_map.get(ele.node_i)
            nj = node_map.get(ele.node_j)
            if ni is None or nj is None:
                continue

            di = step_displacements.get(ni.tag, [0.0, 0.0, 0.0])
            dj = step_displacements.get(nj.tag, [0.0, 0.0, 0.0])

            xi_def = ni.x + di[0] * scale_factor
            yi_def = ni.y + di[1] * scale_factor
            xj_def = nj.x + dj[0] * scale_factor
            yj_def = nj.y + dj[1] * scale_factor

            for sec_data in sections.values():
                ratio = sec_data.get("ratio", 0.0)
                if ratio < 1.0:
                    continue

                loc   = sec_data.get("loc", 0.5)
                x_sec = xi_def + loc * (xj_def - xi_def)
                y_sec = yi_def + loc * (yj_def - yi_def)

                spots.append({
                    'pos':   (x_sec, y_sec),
                    'brush': pg.mkBrush(*self._ratio_to_color(ratio)),
                    'pen':   pg.mkPen(None),
                    'size':  10,
                })

        if spots:
            self.yield_scatter.setData(spots=spots)
            plot_widget.addItem(self.yield_scatter)
            self._in_scene = True

    def _ratio_to_color(self, ratio):
        # 1.0 → amarillo (255,235,59)  |  1.5 → naranja (255,152,0)  |  ≥2.0 → rojo (244,67,54)
        ratio = min(ratio, 2.0)
        if ratio <= 1.5:
            t = (ratio - 1.0) / 0.5
            r = 255
            g = int(235 + t * (152 - 235))
            b = int(59  + t * (0   - 59))
        else:
            t = (ratio - 1.5) / 0.5
            r = int(255 + t * (244 - 255))
            g = int(152 + t * (67  - 152))
            b = int(0   + t * (54  - 0))
        return (r, g, b, 230)
