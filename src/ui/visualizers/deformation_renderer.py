import pyqtgraph as pg
from PyQt6.QtCore import Qt
import math
import numpy as np

class DeformationRenderer:
    def __init__(self):
        self.deformed_items = []
        self.pen_deformed = pg.mkPen(color='#00E5FF', width=2, style=Qt.PenStyle.DashLine)

    def clear(self, plot_widget):
        for item in self.deformed_items:
            plot_widget.removeItem(item)
        self.deformed_items.clear()

    def draw_deformed(self, plot_widget, manager, displacements, scale_factor=10.0):
        self.clear(plot_widget)
        if not displacements: return

        nodes = manager.get_all_nodes()
        elements = manager.get_all_elements()
        node_map = {n.tag: n for n in nodes}

        for el in elements:
            if el.node_i in node_map and el.node_j in node_map:
                ni = node_map[el.node_i]
                nj = node_map[el.node_j]
                
                # Obtener desplazamientos [dx, dy, rz]
                di = displacements.get(ni.tag, [0.0, 0.0, 0.0])
                dj = displacements.get(nj.tag, [0.0, 0.0, 0.0])
                
                # Calcular geometría deformada interpolada
                xs, ys = self._compute_beam_curve(
                    ni, nj, di, dj, scale_factor
                )
                
                # Dibujar curva
                curve = plot_widget.plot(xs, ys, pen=self.pen_deformed)
                self.deformed_items.append(curve)

    def _compute_beam_curve(self, ni, nj, di, dj, scale, num_points=20):
        # 1. Geometría Original
        x1, y1 = ni.x, ni.y
        x2, y2 = nj.x, nj.y
        L = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if L < 1e-9: return [x1, x2], [y1, y2]
        
        # Coseno y Seno directores
        c = (x2 - x1) / L
        s = (y2 - y1) / L
        
        # 2. Transformar desplazamientos globales a locales
        # u = axial, v = transversal
        # di = [dx, dy, theta]
        
        # Nodo I
        ui_local =  di[0]*c + di[1]*s
        vi_local = -di[0]*s + di[1]*c
        ti_local =  di[2] 
        
        # Nodo J
        uj_local =  dj[0]*c + dj[1]*s
        vj_local = -dj[0]*s + dj[1]*c
        tj_local =  dj[2]
        
        # 3. Generar puntos interpolados
        t_vals = np.linspace(0, 1, num_points)
        x_out = []
        y_out = []
        
        for t in t_vals:
            # Interpolación Lineal Axial u(x)
            u_def = (1-t)*ui_local + t*uj_local
            
            # Interpolación Cúbica Transversal v(x) (Hermite)
            h1 = 1 - 3*t**2 + 2*t**3
            h2 = L * (t - 2*t**2 + t**3)
            h3 = 3*t**2 - 2*t**3
            h4 = L * (-t**2 + t**3)
            
            v_def = h1*vi_local + h2*ti_local + h3*vj_local + h4*tj_local
            
            # --- TRANSFORMACIÓN INVERSA (Local -> Global) ---
            # Coordenada 'x' original local a lo largo de la barra
            x_bar = t * L
            
            # Posición original en Global
            x_orig = x1 + x_bar * c
            y_orig = y1 + x_bar * s
            
            # Desplazamiento local escalado
            u_comb = u_def * scale
            v_comb = v_def * scale
            
            # Rotar desplazamiento local escalado a Global
            dx_global = u_comb * c - v_comb * s
            dy_global = u_comb * s + v_comb * c
            
            x_final = x_orig + dx_global
            y_final = y_orig + dy_global
            
            x_out.append(x_final)
            y_out.append(y_final)
            
        return x_out, y_out
