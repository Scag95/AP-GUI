import math
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSlider, QFrame, QCheckBox,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor
from src.analysis.manager import ProjectManager
from src.analysis.sections import FiberSection, AggregatorSection


class _PatchItem(pg.GraphicsObject):
    """Dibuja fibras de hormigón como rectángulos coloreados en coords de datos."""

    def __init__(self):
        super().__init__()
        self._rects  = []
        self._colors = []
        self._br     = QRectF()

    def setup(self, rects_xywh: list):
        """rects_xywh: [(x, y, w, h),...] donde x=z_centroide-dz/2, y=y_centroide-dy/2."""
        self._rects  = [QRectF(x, y, w, h) for x, y, w, h in rects_xywh]
        self._colors = [(220, 220, 220)] * len(rects_xywh)
        if rects_xywh:
            x_min = min(r[0] for r in rects_xywh)
            y_min = min(r[1] for r in rects_xywh)
            x_max = max(r[0] + r[2] for r in rects_xywh)
            y_max = max(r[1] + r[3] for r in rects_xywh)
            self._br = QRectF(x_min, y_min, x_max - x_min, y_max - y_min)
        else:
            self._br = QRectF()
        self.update()

    def update_colors(self, colors: list):
        self._colors = colors
        self.update()

    def boundingRect(self):
        return self._br

    def paint(self, p, *_):
        border = QPen(QColor(80, 80, 80))
        border.setCosmetic(True)   # 1 px fijo independiente del zoom
        border.setWidthF(0.5)
        for rect, col in zip(self._rects, self._colors):
            p.setBrush(QBrush(QColor(*col)))
            p.setPen(border)
            p.drawRect(rect)


class FiberStrainDialog(QWidget):
    """
    Visualiza ε y σ de cada fibra de una FiberSection en cada paso del pushover.
    Los colores de fibras se determinan por estados límite EC8.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Deformaciones de Fibras por Sección")
        self.resize(980, 640)
        self.manager   = ProjectManager.instance()
        self._n_patch      = 0
        self._bar_z        = []
        self._bar_y        = []
        self._bar_s        = []
        self._fiber_labels = []   # pg.TextItem por cada fibra
        self._show_strain = True
        self._show_stress = False
        self._setup_ui()
        self._populate_elements()

    # ── Construcción de UI ────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setSpacing(8)

        # Panel izquierdo
        lf = QFrame()
        lf.setFixedWidth(220)
        left = QVBoxLayout(lf)
        left.setSpacing(6)

        left.addWidget(QLabel("<b>Elemento:</b>"))
        self.combo_element = QComboBox()
        self.combo_element.currentIndexChanged.connect(self._on_element_changed)
        left.addWidget(self.combo_element)

        left.addWidget(QLabel("<b>Punto de integración:</b>"))
        self.combo_sec = QComboBox()
        self.combo_sec.currentIndexChanged.connect(self._on_sec_changed)
        left.addWidget(self.combo_sec)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        left.addWidget(sep)

        left.addWidget(QLabel("<b>Etiquetas visibles:</b>"))
        self.chk_strain = QCheckBox("ε (deformación)")
        self.chk_strain.setChecked(True)
        self.chk_strain.toggled.connect(self._on_labels_toggled)
        left.addWidget(self.chk_strain)

        self.chk_stress = QCheckBox("σ (esfuerzo)")
        self.chk_stress.toggled.connect(self._on_labels_toggled)
        left.addWidget(self.chk_stress)

        left.addSpacing(6)
        left.addWidget(QLabel("<b>Estados límite EC8:</b>"))
        for label, color in [
            ("DL — Cedencia acero",      "#dcb400"),
            ("SL — Hormigón 75% εcu",    "#e66400"),
            ("NC — Hormigón 125% εcu",   "#d20000"),
        ]:
            row = QLabel(f'<span style="background:{color};color:white;'
                         f'padding:1px 6px;border-radius:3px;">■</span>  {label}')
            left.addWidget(row)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        left.addWidget(sep2)

        self.lbl_status = QLabel("")
        self.lbl_status.setWordWrap(True)
        left.addWidget(self.lbl_status)
        left.addStretch()
        root.addWidget(lf)

        # Panel derecho
        right = QVBoxLayout()

        self.plot = pg.PlotWidget()
        self.plot.setBackground('w')
        self.plot.setAspectLocked(True)
        self.plot.showGrid(x=False, y=False)
        self.plot.setLabel('left',   'y [m]')
        self.plot.setLabel('bottom', 'z [m]')

        self._outline     = pg.PlotDataItem(pen=pg.mkPen('k', width=1.5))
        self._patch_item  = _PatchItem()
        self._bar_scatter = pg.ScatterPlotItem(pxMode=False)
        self.plot.addItem(self._outline)
        self.plot.addItem(self._patch_item)
        self.plot.addItem(self._bar_scatter)

        right.addWidget(self.plot)

        slider_row = QHBoxLayout()
        self.lbl_step = QLabel("Paso: 0 / 0")
        self.lbl_step.setFixedWidth(120)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.valueChanged.connect(self._on_step_changed)
        slider_row.addWidget(self.lbl_step)
        slider_row.addWidget(self.slider)
        right.addLayout(slider_row)

        root.addLayout(right)

    # ── Poblar combos ─────────────────────────────────────────────────────────

    def _populate_elements(self):
        from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
        self.combo_element.blockSignals(True)
        self.combo_element.clear()
        for ele in self.manager.get_all_elements():
            if not isinstance(ele, (ForceBeamColumn, ForceBeamColumnHinge)):
                continue
            ni = self.manager.get_node(ele.node_i)
            nj = self.manager.get_node(ele.node_j)
            if ni and nj:
                label = f"Ele {ele.tag}  ({ni.x:.2f},{ni.y:.2f})→({nj.x:.2f},{nj.y:.2f})"
            else:
                label = f"Ele {ele.tag}  (N{ele.node_i}→N{ele.node_j})"
            self.combo_element.addItem(label, ele.tag)
        self.combo_element.blockSignals(False)
        if self.combo_element.count() > 0:
            self._on_element_changed(0)

    def _populate_sec_num(self, ele):
        self.combo_sec.blockSignals(True)
        self.combo_sec.clear()
        n_pts = getattr(ele, 'integration_points', 0)
        for i in range(1, n_pts + 1):
            sec_tag = self.manager._ls_get_sec_tag(ele, i)
            sec     = self.manager.get_section(sec_tag) if sec_tag else None
            name    = sec.name if sec else "?"
            self.combo_sec.addItem(f"Sec. {i}  ({name})", i)
        self.combo_sec.blockSignals(False)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_element_changed(self, index):
        if index < 0:
            return
        ele_tag = self.combo_element.itemData(index)
        ele = self.manager.get_element(ele_tag) if ele_tag is not None else None
        if ele is None:
            return
        self._populate_sec_num(ele)
        self._sync_slider()
        self._rebuild_section()

    def _on_sec_changed(self, _):
        self._rebuild_section()

    def _on_labels_toggled(self, checked: bool):
        self._show_strain = self.chk_strain.isChecked()
        self._show_stress = self.chk_stress.isChecked()
        self._update_colors()

    def _on_step_changed(self, _):
        n = len(self.manager.fiber_history)
        self.lbl_step.setText(f"Paso: {self.slider.value()} / {max(0, n-1)}")
        self._update_colors()

    def _sync_slider(self):
        n = len(self.manager.fiber_history)
        self.slider.blockSignals(True)
        self.slider.setMaximum(max(0, n - 1))
        self.slider.setValue(max(0, n - 1))
        self.slider.blockSignals(False)
        self.lbl_step.setText(f"Paso: {self.slider.value()} / {max(0, n-1)}")

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _current_ele_sec(self):
        ele_tag = self.combo_element.currentData()
        sec_num = self.combo_sec.currentData()
        if ele_tag is None or sec_num is None:
            return None, None, None, None
        ele     = self.manager.get_element(ele_tag)
        sec_tag = self.manager._ls_get_sec_tag(ele, sec_num) if ele else None
        sec     = self.manager.get_section(sec_tag) if sec_tag else None
        return ele_tag, sec_num, ele, sec

    def _draw_outline(self, sec: FiberSection):
        z_out, y_out = [], []
        for p in sec.patches:
            z_out += [p.zI, p.zJ, p.zJ, p.zI, p.zI, float('nan')]
            y_out += [p.yI, p.yI, p.yJ, p.yJ, p.yI, float('nan')]
        self._outline.setData(z_out, y_out, connect="finite")

    def _clear_items(self):
        self._outline.setData([], [])
        self._patch_item.setup([])
        self._bar_scatter.setData([], [])
        self._n_patch = 0
        self._bar_z = []; self._bar_y = []; self._bar_s = []
        for lbl in self._fiber_labels:
            self.plot.removeItem(lbl)
        self._fiber_labels.clear()

    # ── Reconstrucción completa al cambiar elemento/sec ───────────────────────

    def _rebuild_section(self):
        self._clear_items()
        self.lbl_status.setText("")

        ele_tag, sec_num, ele, sec = self._current_ele_sec()
        if ele is None:
            return

        if not isinstance(sec, FiberSection):
            if isinstance(sec, AggregatorSection):
                self.lbl_status.setText(
                    "<i>Sección Aggregator:<br>no tiene fibras individuales.</i>"
                )
            return

        self._draw_outline(sec)

        geom = self.manager.fiber_geometry.get(ele_tag, {}).get(sec_num)
        if geom is None or not self.manager.fiber_history:
            self.lbl_status.setText(
                "<i>Sin datos de pushover.<br>Ejecute análisis primero.</i>"
            )
            self._draw_gray_fallback(sec)
            self.plot.autoRange()
            return

        # Construir rectángulos desde la definición de sección (z de fiberData es 0 en 2D)
        rects, bar_z, bar_y, bar_s = self._build_shapes(sec)
        self._n_patch = len(rects)
        self._bar_z = bar_z; self._bar_y = bar_y; self._bar_s = bar_s

        self._patch_item.setup(rects)
        if bar_z:
            self._bar_scatter.setData(
                x=bar_z, y=bar_y, size=bar_s,
                symbol='o', pen=pg.mkPen('k', width=0.5),
                brush=[pg.mkBrush(220, 220, 220)] * len(bar_z),
            )

        self._setup_labels(rects, bar_z, bar_y)

        self._update_colors()
        self.plot.autoRange()

    def _build_shapes(self, sec: FiberSection):
        """
        Calcula posiciones y tamaños de fibras desde la definición de la sección.
        Orden de bucle: externo=nIy (Y), interno=nIz (Z) — coincide con OpenSees.
        No usa fiberData porque z=0 para todos los elementos en análisis 2D.
        """
        rects = []
        for patch in sec.patches:
            dy = (patch.yJ - patch.yI) / patch.nIy
            dz = (patch.zJ - patch.zI) / patch.nIz
            # Orden OpenSees: externo=nIz (columnas Z), interno=nIy (filas Y)
            for c in range(patch.nIz):
                for r in range(patch.nIy):
                    y_c = patch.yI + (r + 0.5) * dy
                    z_c = patch.zI + (c + 0.5) * dz
                    rects.append((z_c - abs(dz) / 2, y_c - abs(dy) / 2,
                                  abs(dz), abs(dy)))

        bar_z, bar_y, bar_s = [], [], []
        for layer in sec.layers:
            diam = 2.0 * math.sqrt(layer.area_bar / math.pi)
            ys = np.linspace(layer.yStart, layer.yEnd, layer.num_bars)
            zs = np.linspace(layer.zStart, layer.zEnd, layer.num_bars)
            bar_z.extend(zs.tolist())
            bar_y.extend(ys.tolist())
            bar_s.extend([diam] * layer.num_bars)

        return rects, bar_z, bar_y, bar_s

    def _draw_gray_fallback(self, sec: FiberSection):
        """Dibuja la sección en gris (sin datos de pushover)."""
        rects, bar_z, bar_y, bar_s = self._build_shapes(sec)
        self._patch_item.setup(rects)
        if bar_z:
            self._bar_scatter.setData(
                x=bar_z, y=bar_y, size=bar_s,
                symbol='o', pen=pg.mkPen('k', width=0.5),
                brush=[pg.mkBrush(220, 220, 220)] * len(bar_z),
            )

    def _setup_labels(self, patch_rects: list, bar_z: list, bar_y: list):
        """Crea un TextItem centrado en cada fibra (patches + barras)."""
        _STYLE = 'font-size:7pt; font-family:monospace;'

        # Centroides de patches: centro del rectángulo (x+w/2, y+h/2)
        for x, y, w, h in patch_rects:
            lbl = pg.TextItem(anchor=(0.5, 0.5))
            lbl.setHtml(f'<span style="{_STYLE}"></span>')
            lbl.setPos(x + w / 2, y + h / 2)
            self.plot.addItem(lbl)
            self._fiber_labels.append(lbl)

        # Centroides de barras
        for z, y in zip(bar_z, bar_y):
            lbl = pg.TextItem(anchor=(0.5, 0.5))
            lbl.setHtml(f'<span style="{_STYLE}"></span>')
            lbl.setPos(z, y)
            self.plot.addItem(lbl)
            self._fiber_labels.append(lbl)

    # ── Actualizar colores y labels (cada cambio de slider) ───────────────────

    def _update_colors(self):
        ele_tag, sec_num, ele, sec = self._current_ele_sec()
        if not isinstance(sec, FiberSection) or not self.manager.fiber_history:
            return

        step = self.slider.value()
        if step >= len(self.manager.fiber_history):
            return

        fiber_data = self.manager.fiber_history[step].get(ele_tag, {}).get(sec_num)
        if fiber_data is None:
            return

        strains = fiber_data.get("strains", [])
        stresses = fiber_data.get("stresses", [])

        _STYLE = 'font-size:7pt; font-family:monospace;'
        n_patch = self._n_patch

        patch_colors = [
            self._fiber_color(strains[i], i, stresses[i] if i < len(stresses) else 0.0)
            for i in range(n_patch)
        ]
        self._patch_item.update_colors(patch_colors)

        n_bars = len(self._bar_z)
        if n_bars > 0 and len(strains) > n_patch:
            bar_brushes = [
                pg.mkBrush(*self._fiber_color(strains[n_patch + i], n_patch + i, stresses[n_patch + i] if n_patch + i < len(stresses) else 0.0))
                for i in range(n_bars)
            ]
            self._bar_scatter.setData(
                x=self._bar_z, y=self._bar_y, size=self._bar_s,
                symbol='o', pen=pg.mkPen('k', width=0.5),
                brush=bar_brushes,
            )

        show_s = self._show_strain
        show_sigma = self._show_stress

        for i, lbl in enumerate(self._fiber_labels):
            if show_s and show_sigma and i < len(strains) and i < len(stresses):
                lbl.setVisible(True)
                lbl.setHtml(
                    f'<span style="{_STYLE} color:black;">ε={strains[i]:.2e}<br>σ={stresses[i]/1e6:.2f} MPa</span>'
                )
            elif show_s and i < len(strains):
                lbl.setVisible(True)
                lbl.setHtml(f'<span style="{_STYLE} color:black;">ε={strains[i]:.2e}</span>')
            elif show_sigma and i < len(stresses):
                lbl.setVisible(True)
                lbl.setHtml(f'<span style="{_STYLE} color:black;">σ={stresses[i]/1e6:.2f} MPa</span>')
            else:
                lbl.setVisible(False)

    # ── Sincronización con AnimationToolbar del MainWindow ────────────────────

    def connect_to_animation(self, anim_toolbar):
        """Conecta este widget al slider de la AnimationToolbar."""
        anim_toolbar.step_slider.valueChanged.connect(self._on_main_step)

    def _on_main_step(self, value: int):
        """Recibe el paso (0-based) desde el slider del MainWindow."""
        n = len(self.manager.fiber_history)
        if n == 0:
            return
        safe = max(0, min(value, n - 1))
        self.slider.blockSignals(True)
        self.slider.setValue(safe)
        self.slider.blockSignals(False)
        self.lbl_step.setText(f"Paso: {safe} / {max(0, n - 1)}")
        self._update_colors()

    def _fiber_color(self, strain: float, fiber_idx: int, stress: float = 0.0) -> tuple:
        """
        Consulta al manager el estado límite de la fibra y devuelve el color EC8.
        """
        ele_tag = self.combo_element.currentData()
        sec_num = self.combo_sec.currentData()
        if ele_tag is None or sec_num is None:
            return (220, 220, 220)

        ls = self.manager.get_fiber_limit_state(ele_tag, sec_num, fiber_idx, strain)
        if ls == "NC":
            return (210, 0, 0)
        if ls == "SL":
            return (230, 100, 0)
        if ls == "DL":
            return (220, 180, 0)
        return (220, 220, 220)
