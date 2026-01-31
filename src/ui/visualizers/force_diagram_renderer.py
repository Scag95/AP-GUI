import pyqtgraph as pg

class ForceDiagramRenderer:
    def __init__(self):
        self.diagram_items = []
        
    def clear(self, plot_widget):
        for item in self.diagram_items:
            plot_widget.removeItem(item)
        self.diagram_items.clear()

    def draw_diagrams(self, plot_widget, manager, results, diagram_type="Moment"):
        """
        Dibuja diagramas de fuerza.
        :param results: Objeto con reacciones/esfuerzos.
        """
        self.clear(plot_widget)
        # TODO: Implementar lógica de dibujo de diagramas
        pass
