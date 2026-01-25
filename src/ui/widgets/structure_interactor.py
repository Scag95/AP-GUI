import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from src.analysis.manager import ProjectManager

class StructureInteractor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        #Configurar el lienzo gráfico
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=False,y=False, alpha=0.3)
        self.plot_widget.setAspectLocked(True)


        self.layout.addWidget(self.plot_widget)
        self.manager = ProjectManager.instance()
        self.manager.dataChanged.connect(self.refresh_viz)

    def refresh_viz(self):
        self.plot_widget.clear()

        #1. Dibujar Elementos (Lineas)
        elements = self.manager.get_all_elements()

        for ele in elements:
            node_i = self.manager.get_node(ele.node_i)
            node_j = self.manager.get_node(ele.node_j)

            if node_i and node_j:
                #dibujar lineas neagras entre nodos
                self.plot_widget.plot(
                    [node_i.x, node_j.x],
                    [node_i.y, node_j.y],
                    pen=pg.mkPen('k',width=2)
                )
        #2. dibujar nodos(Puntos azules)
        nodes = self.manager.get_all_nodes()
        if nodes:
            x_vals=[n.x for n in nodes]
            y_vals=[n.y for n in nodes]
            data_vals = nodes

            scatter= pg.ScatterPlotItem(
                x=x_vals,
                y=y_vals,
                data=data_vals,
                size=8,
                brush=pg.mkBrush('b'),
                pxMode=True,
                hoverable = True
            )
            scatter.sigClicked.connect(self._on_node_clicked)
            self.plot_widget.addItem(scatter)

        print("[DEBUG] Visualización actualizada.")

    def _on_node_clicked(self, plot_item, points):

        for p in points:
            
            nodo = p.data()
            print(f"Seleccionado Nodo {nodo.tag} (x={nodo.x}, y={nodo.y})")