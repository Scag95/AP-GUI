from PyQt6.QtCore import Qt
import pyqtgraph as pg

class ModelRenderer:
    def __init__(self):
        self.node_items = {} # map tag -> ScatterPlotItem (spot)
        self.element_items = {} # map tag -> PlotCurveItem
        self.labels = []
        # Estilos
        self.pen_element = pg.mkPen(color='k', width=2)
        self.brush_node = pg.mkBrush(color='#2196F3')
        self.pen_node = pg.mkPen(color='#FFFFFF', width=1)
        self.size_node = 10

        # Para todos los nodos juntos (más eficiente)
        self.scatter_nodes = pg.ScatterPlotItem(
            size=self.size_node, 
            brush=self.brush_node, 
            pen=self.pen_node,
            hoverable=True
        )
        self.scatter_nodes.setZValue(100)

    def attach(self, plot_widget):
        """Añade los items base al plot."""
        plot_widget.addItem(self.scatter_nodes)

    def clear(self, plot_widget):
        """Limpia elementos dinámicos (barras, etiquetas). El scatter se limpia vaciando datos."""
        for item in self.element_items.values():
            plot_widget.removeItem(item)
        self.element_items.clear()
        
        for lbl in self.labels:
            plot_widget.removeItem(lbl)
        self.labels.clear()
        
        self.scatter_nodes.setData([], []) # Limpiar puntos

    def draw_structure(self, plot_widget, manager, show_labels=False):
        self.clear(plot_widget)
        
        nodes = manager.get_all_nodes()
        elements = manager.get_all_elements()
        
        # 1. Dibujar Elementos (Líneas)
        # Mapa rápido de nodos
        node_map = {n.tag: n for n in nodes}
        
        for el in elements:
            if el.node_i in node_map and el.node_j in node_map:
                ni = node_map[el.node_i]
                nj = node_map[el.node_j]
                
                # Crear línea usando .plot() directamente (más seguro)
                curve = plot_widget.plot(
                    [ni.x, nj.x], [ni.y, nj.y], 
                    pen=self.pen_element,
                    clickable=True
                )
                # curve.setData(antialias=True) # Opcional
                # Guardamos referencia (para clicks futuros)
                # curve.ele_tag = el.tag 
                
                # plot_widget.addItem(curve) # Ya no hace falta, plot() lo añade
                self.element_items[el.tag] = curve
                
                # Etiqueta de elemento
                if show_labels:
                    mid_x = (ni.x + nj.x)/2
                    mid_y = (ni.y + nj.y)/2
                    text = pg.TextItem(text=str(el.tag), color='k', anchor=(0.5, 0.5))
                    text.setPos(mid_x, mid_y)
                    plot_widget.addItem(text)
                    self.labels.append(text)

        # 2. Dibujar Nodos (Scatter único)
        x_vals = []
        y_vals = []
        data_vals = [] # Guardaremos el tag aquí
        
        for n in nodes:
            x_vals.append(n.x)
            y_vals.append(n.y)
            data_vals.append(n.tag)
            
            # Etiqueta de nodo
            if show_labels:
                text = pg.TextItem(text=str(n.tag), color='#2196F3', anchor=(0, 1))
                text.setPos(n.x, n.y)
                plot_widget.addItem(text)
                self.labels.append(text)

        # Actualizar Scatter
        self.scatter_nodes.setData(x_vals, y_vals, data=data_vals)

    def highlight_node(self, node_tag, color='#FFCC00'):
        # TODO: Implementar resaltado
        pass
