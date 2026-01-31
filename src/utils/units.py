from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

class UnitType(Enum):
    LENGTH = "Length"
    SECTION_DIM = "Section"
    FORCE = "Force"
    MOMENT = "Moment"
    STRESS = "Stress"
    DENSITY = "Density"
    DISTRIBUTED_FORCE = "DistributedForce"

class UnitManager(QObject):
    _instance = None
    unitsChanged = pyqtSignal()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        if hasattr(self, "initialized"): return
        self.initialized = True

        # --- DEFINICIÓN DE UNIDADES BASE (SI PURO: m, N, Pa, kg) ---
        self.factors = {
            UnitType.LENGTH: {
                "m": 1.0,           # BASE
                "cm": 0.01,
                "mm": 0.001,
                "ft": 0.3048,
                "in": 0.0254
            },
            UnitType.SECTION_DIM: {
                "m": 1.0,           # BASE
                "cm": 0.01,
                "mm": 0.001,
                "ft": 0.3048,
                "in": 0.0254
            },
            UnitType.FORCE: {
                "N": 1.0,           # BASE
                "kN": 1000.0,
                "MN": 1000000.0,
                "kgf": 9.80665,
                "Ton": 9806.65,
                "kips": 4448.22
            },
            UnitType.MOMENT: {
                "Nm": 1.0,          # BASE
                "kNm": 1000.0,
                "Ton-m": 9806.65,
                "kip-ft": 1355.8
            },
            UnitType.STRESS: {
                "Pa": 1.0,          # BASE (N/m2)
                "kPa": 1000.0,
                "MPa": 1000000.0,
                "GPa": 1000000000.0,
                "ksi": 6894757.0,
                "psi": 6894.757
            },
            UnitType.DENSITY: {
                "kg/m3": 1.0,        # BASE
                "Ton/m3": 1000.0,
                "g/cm3": 1000.0,
                "lb/ft3": 16.0185
            },
            UnitType.DISTRIBUTED_FORCE: {
                "N/m": 1.0,          # BASE
                "kN/m": 1000.0,
                "kgf/m": 9.80665,
                "Ton/m": 9806.65,
                "kips/ft": 14593.9
            }
        }

        self.current_units = {
            UnitType.LENGTH: "m",
            UnitType.SECTION_DIM: "mm",
            UnitType.FORCE: "kN",
            UnitType.MOMENT: "kNm",
            UnitType.STRESS: "MPa",
            UnitType.DENSITY: "kg/m3",
            UnitType.DISTRIBUTED_FORCE: "kN/m"
        }

    def get_current_unit(self, unit_type: UnitType):
        """Devuelve el string de la unidad actual (ej. 'mm')"""
        return self.current_units.get(unit_type, "")

    def set_unit(self, unit_type: UnitType, unit_name: str):
        """Cambia la unidad actual para un tipo dado."""
        if unit_name in self.factors[unit_type]:
            self.current_units[unit_type] = unit_name
            self.unitsChanged.emit()
    
    def to_base(self, value, unit_type: UnitType):
        """Convierte de la unidad actual a la unidad base."""
        unit = self.current_units[unit_type]
        factor = self.factors[unit_type][unit]
        return value * factor

    def from_base(self, value, unit_type: UnitType):
        """Conviente de la unidad base a la unidad actual."""
        unit = self.current_units[unit_type]
        factor = self.factors[unit_type][unit]
        if factor == 0: return 0
        return value / factor
        
    def get_avaliable_units(self, unit_type: UnitType):
        """Devuelve lista de unidades disponebles para comboboxes."""
        return list(self.factors[unit_type].keys())
