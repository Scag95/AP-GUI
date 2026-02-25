from PyQt6.QtCore import QObject, pyqtSignal
from src.analysis.manager import ProjectManager

class ScaleManager(QObject):
    _instance = None
    
    # Señal que emite el factor combinado REAL para los renderizadores (Ej: 0.0003)
    scale_changed = pyqtSignal(str, float)
    
    # Señal que emite el factor relativo del USUARIO para el panel visual (Ej: 1.0)
    multiplier_changed = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()
        
        # Escalas base (Cálculo interno geométrico)
        self._base_scales = {
            'deformation': 10.0,
            'moment': 0.003,
            'shear': 0.003,
            'axial': 0.003,
            'load': 0.0003,
            'reaction': 0.3,
            'node_size': 10.0
        }
        
        # Multiplicadores del usuario (Lo que ve en el Panel UI, por defecto 1.0)
        self._user_multipliers = {k: 1.0 for k in self._base_scales.keys()}
        
        # Guardamos Bounding Box del modelo para auto-escalado
        self.model_dim_max = 3 

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_user_multiplier(self, scale_type, multiplier):
        """El Panel llama a esto. Modificamos el x1.0 del usuario."""
        if scale_type in self._user_multipliers:
            self._user_multipliers[scale_type] = multiplier
            # Notificamos a la UI del cambio relativo
            self.multiplier_changed.emit(scale_type, multiplier)
            # Notificamos a los renderers del nuevo valor total absoluto
            total_scale = self.get_scale(scale_type)
            self.scale_changed.emit(scale_type, total_scale)

    def get_user_multiplier(self, scale_type):
        """Devuelve el valor relativo 1.0 para el Panel"""
        return self._user_multipliers.get(scale_type, 1.0)

    def set_base_scale(self, scale_type, value):
        """El motor de AutoCAD/Auto-escalado llama a esto. Mantiene multiplicador intocable"""
        if scale_type in self._base_scales:
            self._base_scales[scale_type] = value
            # Al cambiar la base, la escala total cambia automáticamente
            total_scale = self.get_scale(scale_type)
            self.scale_changed.emit(scale_type, total_scale)

    def get_scale(self, scale_type):
        """Devuelve la escala física REAL a los renderizadores (Base * Multiplicador)"""
        base = self._base_scales.get(scale_type, 1.0)
        mult = self._user_multipliers.get(scale_type, 1.0)
        return base * mult

    def autocalculate_scales(self):
        """
        Calcula escalas sugeridas basándose en el tamaño del modelo.
        """
        manager = ProjectManager.instance()
        nodes = manager.get_all_nodes()
        
        if not nodes: return

        xs = [n.x for n in nodes]
        ys = [n.y for n in nodes]
        width = max(xs) - min(xs) if xs else 0
        height = max(ys) - min(ys) if ys else 0
        
        L_char = max(width, height)
        if L_char < 1.0: L_char = 1.0 
        
        self.model_dim_max = L_char
        
        # Heurísticas
        base_diagram = L_char * 0.003 # 15% del tamaño para diagramas unitarios
        
        # Actualizamos solo la BASE (física). El multiplicador visual se queda donde el usuario lo puso (ej 1.0)
        self.set_base_scale('moment', base_diagram)
        self.set_base_scale('shear', base_diagram)
        self.set_base_scale('deformation', 50.0) 
        self.set_base_scale('load', L_char * 0.00001)
        self.set_base_scale('node_size', 6.0) 
        
        print(f"[ScaleManager] Escalas base recalculadas para L={L_char:.2f}")