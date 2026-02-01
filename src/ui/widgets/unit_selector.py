from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt
from src.utils.units import UnitManager, UnitType

class UnitSelectorWidget(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus) # Para no robar foco al escribir comandos
        
        # Estilo oscuro integrado
        self.setStyleSheet("""
            QComboBox {
                background-color: rgba(45, 45, 45, 180);
                color: #ffffff;
                border: none;
                border-top: 1px solid #3e3e3e;
                padding: 4px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #ffffff;
                selection-background-color: #555555;
            }
        """)

        # Definir Presets
        # Formato: (Label, {UnitType: UnitName})
        self.presets = [
            ("kN, m", {
                UnitType.FORCE: "kN",
                UnitType.LENGTH: "m",
                UnitType.SECTION_DIM: "mm", 
                UnitType.MOMENT: "kNm",
                UnitType.STRESS: "MPa",
                UnitType.DISTRIBUTED_FORCE: "kN/m"
            }),
            ("N, mm", {
                UnitType.FORCE: "N",
                UnitType.LENGTH: "mm",
                UnitType.SECTION_DIM: "mm",
                UnitType.MOMENT: "Nm", 
                UnitType.STRESS: "MPa",
                UnitType.DISTRIBUTED_FORCE: "N/mm"
            }),
            ("Ton, m", {
                UnitType.FORCE: "Ton",
                UnitType.LENGTH: "m",
                UnitType.SECTION_DIM: "m", 
                UnitType.MOMENT: "Ton-m",
                UnitType.STRESS: "kg/cm2", # Fallback to base or simmilar if not exists, but let's stick to simple
                UnitType.DISTRIBUTED_FORCE: "Ton/m"
            }),
            ("kips, ft", {
                UnitType.FORCE: "kips",
                UnitType.LENGTH: "ft",
                UnitType.SECTION_DIM: "in",
                UnitType.MOMENT: "kip-ft",
                UnitType.STRESS: "ksi",
                UnitType.DISTRIBUTED_FORCE: "kips/ft"
            })
        ]

        # Poblar ComboBox
        for label, _ in self.presets:
            self.addItem(label)
            
        # Conectar señal
        self.currentIndexChanged.connect(self._apply_preset)
        
        # Aplicar el primero por defecto
        self.setCurrentIndex(0)

    def _apply_preset(self, index):
        if index < 0 or index >= len(self.presets): return
        
        _, units_map = self.presets[index]
        um = UnitManager.instance()
        
        # Bloquear señales para evitar 5 refrescos seguidos
        um.blockSignals(True)
        try:
            for u_type, u_name in units_map.items():
                # Verificar disponibilidad básica antes de setear (resiliencia)
                if u_name in um.factors.get(u_type, {}):
                    um.set_unit(u_type, u_name)
        finally:
            um.blockSignals(False)
            # Emitir señal manual de cambio
            um.unitsChanged.emit()
            print(f"[Units] Preset aplicado: {self.currentText()}")
