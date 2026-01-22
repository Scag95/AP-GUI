import pyqtgraph as pg
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtCore import Qt
import numpy as np

class SectionPreview(pg.PlotWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):

        #1. estetica básica
        self.setBackground('w')
        self.showGrid(x=False, y=False, alpha=0.3)
        self.setAspectLocked(True)


        # 2. EJES DE COORDENADAS (Estilo SAP2000)
        L = 0.5 
                # Eje Y (Vertical): línea de (0, -L) a (0, L)
        self.axis_y = pg.PlotDataItem(
            [0, 0], [-L, L], 
            pen=pg.mkPen('b', width=1)
        )
        # Eje Z (Horizontal): línea de (-L, L) a (0, 0)
        # Ojo: En pyqtgraph axes son (X, Y). Nuestro Z es X gráfico.
        self.axis_z = pg.PlotDataItem(
            [-L, L], [0, 0], 
            pen=pg.mkPen('g', width=1)
        )
        self.addItem(self.axis_y)
        self.addItem(self.axis_z)
        
        # Etiquetas de los ejes simulando la imagen (2 arriba, 3/z a la izquierda)
        # Nota: En OpenSees local Y suele ser eje 2, local Z suele ser eje 3.
        self.label_y = pg.TextItem("y", color='b', anchor=(0.5, 1))
        self.label_z = pg.TextItem("z", color='g', anchor=(0, 0.5))
        
        # Ocultar ejes del marco (números)
        self.showAxis('left', False)
        self.showAxis('bottom', False)

        self.label_y.setPos(0, L) 
        self.label_z.setPos(L, 0)
        
        self.addItem(self.label_y)
        self.addItem(self.label_z)


        self.concrete_outline = pg.PlotDataItem(pen=pg.mkPen('k',width=2))
        self.steel_bars = pg.ScatterPlotItem(size=10, pen=pg.mkPen('k'), brush=pg.mkBrush('r'))

        #Añadir los items vacíos al gráfico
        self.addItem(self.concrete_outline)
        self.addItem(self.steel_bars)

    def plot_section(self,fiber_section):
        #1. Dibujar la seccion(Concreto)
        z_outline = []
        y_outline = []

        for patch in fiber_section.patches:

            z_pts = [patch.zI, patch.zJ, patch.zJ, patch.zI, patch.zI]
            y_pts = [patch.yI, patch.yI, patch.yJ, patch.yJ, patch.yI]

            z_outline.extend(z_pts)
            y_outline.extend(y_pts)

            z_outline.append(np.nan)
            y_outline.append(np.nan)

        self.concrete_outline.setData(z_outline, y_outline, connect="finite")
     
        # 2. Dibujar Barras (Acero)
        z_bars = []
        y_bars = []


        for layer in fiber_section.layers:
            if layer.num_bars > 0:
                y_pts = np.linspace(layer.yStart, layer.yEnd, layer.num_bars)
                z_pts = np.linspace(layer.zStart, layer.zEnd, layer.num_bars)

                y_bars.extend(y_pts)
                z_bars.extend(z_pts)

        self.steel_bars.setData(z_bars, y_bars)

    
        