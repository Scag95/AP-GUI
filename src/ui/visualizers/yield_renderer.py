import math
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

            ele_length = math.sqrt((nj.x - ni.x) ** 2 + (nj.y - ni.y) ** 2)

            for sec_data in sections.values():
                ratio = sec_data.get("ratio", 0.0)
                if ratio < 1.0:
                    continue

                loc      = sec_data.get("loc", 0.5)
                loc_frac = (loc / ele_length) if ele_length > 0 else 0.5
                x_sec    = xi_def + loc_frac * (xj_def - xi_def)
                y_sec    = yi_def + loc_frac * (yj_def - yi_def)

                ls = sec_data.get("limit_state", "DL")
                spots.append({
                    'pos':   (x_sec, y_sec),
                    'brush': pg.mkBrush(*self._ls_to_color(ls)),
                    'pen':   pg.mkPen(None),
                    'size':  10,
                })

        if spots:
            self.yield_scatter.setData(spots=spots)
            plot_widget.addItem(self.yield_scatter)
            self._in_scene = True

    def _ls_to_color(self, ls: str):
        if ls == "NC":
            return (210,   0,   0, 230)   # rojo
        elif ls == "SL":
            return (230, 100,   0, 230)   # naranja
        else:                              # DL
            return (220, 180,   0, 230)   # amarillo
