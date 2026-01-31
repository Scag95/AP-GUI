from PyQt6.QtWidgets import QDoubleSpinBox
from src.utils.units import UnitManager, UnitType

class UnitSpinBox(QDoubleSpinBox):

    def __init__(self, unit_type: UnitType, parent=None):
        super().__init__(parent) # Correccion: Quitado : al final
        self.unit_type = unit_type
        self.manager = UnitManager.instance()

        #Almacenamos e valor base "Verdadero" internamente
        self._base_value = 0.0

        #Conectamos a la señal goblas de cambio de unidades
        self.manager.unitsChanged.connect(self._update_display)

        self.valueChanged.connect(self._on_value_changed_internal)

        #Configuración inicial
        self._update_display()

        # Mejorar UX: seleccionar todo al hacer click
        self.setGroupSeparatorShown(True)

    def _on_value_changed_internal(self, val):
        #Cuando el valor visual cambia (por usuario o programa), recalculamos el valor base y lo guardamos.
        self._base_value = self.manager.to_base(val, self.unit_type)

    
    def _update_display(self):
        """Actualiza el sufijo y ajusta el valor según la nueva unidad"""
        # 1. Obtenemos la nueva etiqueta
        unit_label = self.manager.get_current_unit(self.unit_type)
        self.setSuffix(f" {unit_label}")

        # 2. Calculamos el nuevo valor visual desde el base guardado
        new_visual = self.manager.from_base(self._base_value,self.unit_type)

        # 3. actualizamos sin dispalar señales 
        self.blockSignals(True)
        self.setValue(new_visual)
        self.blockSignals(False)


    def get_value_base(self):
        """Devuelve el valor en unidades CANÓNICAS (m, kN, etc)"""
        return self._base_value

    def set_value_base(self, base_value):
        """Establece el valor usando unidades CANÓNICAS."""
        self._base_value = base_value
        visual_value = self.manager.from_base(base_value, self.unit_type)
        self.blockSignals(True)
        self.setValue(visual_value)
        self.blockSignals(False)

    # --- Métodos extra para validación ---
    def validate(self, text, pos):
        return super().validate(text, pos)