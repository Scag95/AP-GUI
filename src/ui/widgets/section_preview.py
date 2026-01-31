import pyqtgraph as pg
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtCore import Qt
import numpy as np
import math

class SectionPreview(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # 1. Estética básica
        self.setBackground('w')
        self.showGrid(x=False, y=False, alpha=0.3)
        self.setAspectLocked(True)
        
        # Ocultar ejes del marco
        self.showAxis('left', False)
        self.showAxis('bottom', False)

        # 2. ELEMENTOS GRÁFICOS
        # Contorno hormigón
        self.concrete_outline = pg.PlotDataItem(pen=pg.mkPen('k', width=2))
        self.addItem(self.concrete_outline)

        # Barras de acero
        # pxMode=False: El tamaño (size) se interpreta en unidades del gráfico (metros), no píxeles.
        self.steel_bars = pg.ScatterPlotItem(
            pen=pg.mkPen('k', width=0), 
            brush=pg.mkBrush('r'),
            pxMode=False 
        )
        self.addItem(self.steel_bars)

        # 3. EJES (Flechas tipo Load)
        # Usamos pxMode=False para que escalen con el zoom
        self.arrow_y = pg.ArrowItem(pen=pg.mkPen('b', width=1), brush='b', pxMode=False)
        self.arrow_z = pg.ArrowItem(pen=pg.mkPen('g', width=1), brush='g', pxMode=False)
        
        self.addItem(self.arrow_y)
        self.addItem(self.arrow_z)

        # Etiquetas
        self.label_y = pg.TextItem("y", color='b', anchor=(0.5, 1))
        self.label_z = pg.TextItem("z", color='g', anchor=(0, 0.5))
        self.addItem(self.label_y)
        self.addItem(self.label_z)

    def plot_section(self, fiber_section):
        # 1. Dibujar Contorno (Hormigón)
        z_outline = []
        y_outline = []
        
        max_dim = 0.1 

        for patch in fiber_section.patches:
            z_pts = [patch.zI, patch.zJ, patch.zJ, patch.zI, patch.zI]
            y_pts = [patch.yI, patch.yI, patch.yJ, patch.yJ, patch.yI]
            
            z_outline.extend(z_pts)
            y_outline.extend(y_pts)
            
            z_outline.append(np.nan)
            y_outline.append(np.nan)
            
            # Calcular dimensiones para escalar ejes
            dims = [abs(patch.zI), abs(patch.zJ), abs(patch.yI), abs(patch.yJ)]
            curr_max = max(dims) if dims else 0
            max_dim = max(max_dim, curr_max)

        self.concrete_outline.setData(z_outline, y_outline, connect="finite")

        # 2. Dibujar Barras (Acero)
        z_bars = []
        y_bars = []
        sizes = []

        for layer in fiber_section.layers:
            if layer.num_bars > 0:
                y_pts = np.linspace(layer.yStart, layer.yEnd, layer.num_bars)
                z_pts = np.linspace(layer.zStart, layer.zEnd, layer.num_bars)
                
                # Calcular diámetro basado en área
                diam = 2.0 * math.sqrt(layer.area_bar / math.pi)
                
                z_bars.extend(z_pts)
                y_bars.extend(y_pts)
                sizes.extend([diam] * layer.num_bars)

        self.steel_bars.setData(z_bars, y_bars, size=sizes)

        # 3. Ajustar Ejes Dinámicamente
        if max_dim == 0: max_dim = 0.1
        axis_len = max_dim * 0.5
        head_len = axis_len * 0.15
        tail_len = axis_len - head_len
        tail_width = max_dim * 0.002
        if tail_width < 0.001: tail_width = 0.001
        
        # Eje Y (Vertical - Azul) - Apunta Arriba (+Y)
        # Nota: ArrowItem a 0 grados apunta a **IZQUIERDA** por defecto en pyqtgraph.
        # -90 grados (270) apunta ARRIBA.
        self.arrow_y.setPos(0, axis_len)
        self.arrow_y.setStyle(
            angle=-90, 
            headLen=head_len,
            tailLen=tail_len,
            tailWidth=tail_width,
            brush='b', pen='b'
        )
        
        # Eje Z (Horizontal - Verde) - Apunta Derecha (+Z)
        # 0 grados apunta IZQUIERDA. 180 grados apunta DERECHA.
        self.arrow_z.setPos(axis_len, 0)
        self.arrow_z.setStyle(
            angle=180, 
            headLen=head_len,
            tailLen=tail_len,
            tailWidth=tail_width,
            brush='g', pen='g'
        )
        
        # Etiquetas
        self.label_y.setPos(0, axis_len + head_len*0.5)
        self.label_z.setPos(axis_len + head_len*0.5, 0)

        # Auto-ajustar vista
        self.autoRange()