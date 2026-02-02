from PyQt6.QtCore import QObject, pyqtSignal
from src.analysis.manager import ProjectManager

class ScaleManager(QObject):
    _instance = None
    
    # Señal que se emite cuando CUALQUIER escala cambia
    scale_changed = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()
        # Factores de escala por defecto
        self._scales = {
            'deformation': 50.0,
            'moment': 0.003,
            'shear': 0.003,
            'axial': 0.003,
            'load': 0.3,
            'reaction': 0.3,
            'node_size': 10.0
        }
        
        # Guardamos Bounding Box del modelo para auto-escalado
        self.model_dim_max = 3 

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_scale(self, scale_type, value):
        if scale_type in self._scales:
            self._scales[scale_type] = value
            self.scale_changed.emit(scale_type, value)

    def get_scale(self, scale_type):
        return self._scales.get(scale_type, 1.0)

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
        
        self.set_scale('moment', base_diagram) # Ojo: Mz suele ser grande numéricamente, esto requerirá ajuste dinámico según Max Mz
        self.set_scale('shear', base_diagram)
        self.set_scale('deformation', 50.0) 
        self.set_scale('load', L_char * 0.01)
        self.set_scale('node_size', 10.0) 
        
        print(f"[ScaleManager] Escalas recalculadas para L={L_char:.2f}")