import math
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt
from src.utils.scale_manager import ScaleManager

_LS_RANK     = {"DL": 1, "SL": 2, "NC": 3}
_RANK_TO_LS  = {1: "DL", 2: "SL", 3: "NC"}

_COLOR = {
    "DL": (220, 180,   0, 230),
    "SL": (230, 100,   0, 230),
    "NC": (210,   0,   0, 230),
}


def _make_scatter(color: tuple) -> pg.ScatterPlotItem:
    sc = pg.ScatterPlotItem(
        pxMode=True, symbol='o', size=8,
        pen=pg.mkPen(None), brush=pg.mkBrush(*color),
    )
    sc.setZValue(200)
    return sc


class YieldRenderer:

    def __init__(self):
        # Un ScatterPlotItem por color — brush fijo, actualización por array numpy
        self._scatter = {ls: _make_scatter(col) for ls, col in _COLOR.items()}
        self._in_scene: set         = set()      # qué LS están añadidos al plot
        self._cross_items: list     = []
        self._max_limit_state: dict = {}         # {(ele_tag, sec_num): "NC"|"SL"|"DL"}
        self._last_step: int        = -1
        self._node_map: dict        = {}         # caché de nodos (válida durante animación)

    # ── Gestión de escena ────────────────────────────────────────────────────

    def clear(self, plot_widget):
        for ls in list(self._in_scene):
            plot_widget.removeItem(self._scatter[ls])
        self._in_scene.clear()

    def reset_limit_state_history(self):
        self._max_limit_state.clear()
        self._last_step = -1
        self._node_map.clear()

    def clear_crosses(self, plot_widget):
        for item in self._cross_items:
            plot_widget.removeItem(item)
        self._cross_items.clear()

    # ── Acumulación de estados (sin dibujar) ─────────────────────────────────

    def _accumulate_limit_states(self, step_yield_data: dict):
        mls = self._max_limit_state
        for ele_tag, sections in step_yield_data.items():
            for sec_num, fibers in sections.items():
                sec_key  = (ele_tag, sec_num)
                cur_rank = _LS_RANK.get(mls.get(sec_key), 0)
                for fiber in fibers:
                    r = _LS_RANK.get(fiber.get("limit_state"), 0)
                    if r > cur_rank:
                        cur_rank = r
                if cur_rank > 0:
                    mls[sec_key] = _RANK_TO_LS[cur_rank]

    # ── Dibujado principal ───────────────────────────────────────────────────

    def draw_yield_state(self, plot_widget, manager,
                         step_yield_data, step_displacements,
                         step_index: int = None):
        """
        Pinta puntos de fluencia sobre la forma deformada.

        step_yield_data   : { ele_tag: { sec_num: [{ratio, loc, limit_state,...}] } }
        step_displacements: { node_tag: [dx, dy, rz] }
        step_index        : índice 0-based en yield_history; permite scrubbing inverso.
        """
        # ── Gestión de scrubbing inverso ─────────────────────────────────────
        if step_index is not None:
            if step_index <= self._last_step:
                self._max_limit_state.clear()
                for i in range(step_index):
                    if i < len(manager.yield_history):
                        self._accumulate_limit_states(manager.yield_history[i])
            self._last_step = step_index

        if not step_yield_data:
            self._flush_scatter(plot_widget, {}, {})
            return

        # Acumular el paso actual
        self._accumulate_limit_states(step_yield_data)

        # ── Calcular posiciones ───────────────────────────────────────────────
        scale_factor = ScaleManager.instance().get_scale('deformation')

        # Caché de nodos: se reconstruye solo si está vacía (una vez por sesión)
        if not self._node_map:
            self._node_map = {n.tag: n for n in manager.get_all_nodes()}
        node_map = self._node_map

        xs: dict = {"DL": [], "SL": [], "NC": []}
        ys: dict = {"DL": [], "SL": [], "NC": []}

        for ele_tag, sections in step_yield_data.items():
            ele = manager.get_element(ele_tag)
            if ele is None:
                continue

            ni = node_map.get(ele.node_i)
            nj = node_map.get(ele.node_j)
            if ni is None or nj is None:
                continue

            di = step_displacements.get(ni.tag, (0.0, 0.0, 0.0))
            dj = step_displacements.get(nj.tag, (0.0, 0.0, 0.0))

            xi_def = ni.x + di[0] * scale_factor
            yi_def = ni.y + di[1] * scale_factor
            xj_def = nj.x + dj[0] * scale_factor
            yj_def = nj.y + dj[1] * scale_factor

            dx = nj.x - ni.x
            dy = nj.y - ni.y
            ele_length = math.sqrt(dx * dx + dy * dy)

            for sec_num, fibers in sections.items():
                ls = self._max_limit_state.get((ele_tag, sec_num), "DL")
                xl = xs[ls]
                yl = ys[ls]

                for fiber in fibers:
                    if fiber.get("ratio", 0.0) < 1.0:
                        continue
                    loc = fiber.get("loc", 0.5)
                    t   = (loc / ele_length) if ele_length > 0 else 0.5
                    xl.append(xi_def + t * (xj_def - xi_def))
                    yl.append(yi_def + t * (yj_def - yi_def))

        self._flush_scatter(plot_widget, xs, ys)

    def _flush_scatter(self, plot_widget, xs: dict, ys: dict):
        """Actualiza los 3 ScatterPlotItems con arrays numpy; gestiona addItem/removeItem."""
        for ls, sc in self._scatter.items():
            x_list = xs.get(ls, [])
            if x_list:
                sc.setData(x=np.asarray(x_list, dtype=np.float64),
                           y=np.asarray(ys[ls],  dtype=np.float64))
                if ls not in self._in_scene:
                    plot_widget.addItem(sc)
                    self._in_scene.add(ls)
            else:
                if ls in self._in_scene:
                    plot_widget.removeItem(sc)
                    self._in_scene.discard(ls)
                sc.setData(x=np.empty(0), y=np.empty(0))

    # ── Cruces de San Andrés ─────────────────────────────────────────────────

    def draw_frozen_floors(self, plot_widget, frozen_floors, frozen_columns,
                           step_displacements, scale_factor, manager):
        """Dibuja cruces de San Andrés usando los pares diagonales capturados al freezear."""
        self.clear_crosses(plot_widget)
        if not frozen_floors or not frozen_columns:
            return

        if not self._node_map:
            self._node_map = {n.tag: n for n in manager.get_all_nodes()}
        node_map = self._node_map

        pen = pg.mkPen(color=(180, 30, 30, 210), width=2, style=Qt.PenStyle.DashLine)

        for y_level in frozen_floors:
            for (ni_tag, nj_tag) in frozen_columns.get(y_level, []):
                ni = node_map.get(ni_tag)
                nj = node_map.get(nj_tag)
                if not ni or not nj:
                    continue

                di = step_displacements.get(ni_tag, (0.0, 0.0, 0.0))
                dj = step_displacements.get(nj_tag, (0.0, 0.0, 0.0))

                xi = ni.x + di[0] * scale_factor
                yi = ni.y + di[1] * scale_factor
                xj = nj.x + dj[0] * scale_factor
                yj = nj.y + dj[1] * scale_factor

                line = pg.PlotDataItem([xi, xj], [yi, yj], pen=pen)
                line.setZValue(190)
                plot_widget.addItem(line)
                self._cross_items.append(line)
