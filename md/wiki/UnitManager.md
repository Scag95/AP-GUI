# UnitManager

Singleton + QObject que gestiona el sistema de unidades de la aplicación.

## Clase
`UnitManager`

## Propósito
Gestiona conversión de unidades y notifica cambios a toda la UI.

## Singleton
```python
UnitManager.instance()
```

## Tipos de Unidades

```python
class UnitType(Enum):
    LENGTH = "Length"
    SECTION_DIM = "Section"
    FORCE = "Force"
    MOMENT = "Moment"
    STRESS = "Stress"
    DENSITY = "Density"
    DISTRIBUTED_FORCE = "DistributedForce"
    ACCELERATION = "Acceleration"
    MASS = "Mass"
```

## Unidades Disponibles por Tipo

| Tipo | Unidades |
|------|----------|
| LENGTH, SECTION_DIM | m, cm, mm, ft, in |
| FORCE | N, kN, MN, kgf, Ton, kips |
| MOMENT | Nm, kNm, Ton-m, kip-ft |
| STRESS | Pa, kPa, MPa, GPa, ksi, psi |
| DENSITY | kg/m3, Ton/m3, g/cm3, lb/ft3 |
| DISTRIBUTED_FORCE | N/m, kN/m, kgf/m, Ton/m, kips/ft, N/mm |
| ACCELERATION | m/s2, cm/s2, mm/s2, ft/s2, in/s2, g |
| MASS | kg, T, g, lb |

## Unidades Actuales (Defaults)

```python
current_units = {
    UnitType.LENGTH: "m",
    UnitType.SECTION_DIM: "mm",
    UnitType.FORCE: "kN",
    UnitType.MOMENT: "kNm",
    UnitType.STRESS: "MPa",
    UnitType.DENSITY: "kg/m3",
    UnitType.DISTRIBUTED_FORCE: "kN/m",
    UnitType.ACCELERATION: "m/s2",
    UnitType.MASS: "kg"
}
```

## Funciones

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `instance()` | Obtiene singleton | UnitManager |
| `get_current_unit(type)` | Retorna unidad actual (ej "mm") | str |
| `set_unit(type, name)` | Cambia unidad y emite `unitsChanged` | None |
| `to_base(value, type)` | Convierte de actual a base (SI) | float |
| `from_base(value, type)` | Convierte de base a actual | float |
| `get_avaliable_units(type)` | Lista de unidades disponibles | list |

## Señales

```python
unitsChanged = pyqtSignal()  # Emitido cuando cambia cualquier unidad
```

## Ejemplo

```python
um = UnitManager.instance()
# Mostrar en UI
length_unit = um.get_current_unit(UnitType.LENGTH)  # "mm"
# Convertir input de usuario a base
base_value = um.to_base(300, UnitType.LENGTH)  # 0.3 (en metros)
# Convertir de base a display
display_value = um.from_base(0.3, UnitType.LENGTH)  # 300
```

## Relaciones

```
UnitManager
├── ProjectManager ──► Accede a singleton
├── UnitSpinBox ──► Convierte valores de entrada
├── MainWindow ──► Reconecta señal
└── toda la UI ──► Recibe señal unitsChanged
```

## Relacionado Con

- [[MainWindow]] - Se reconecta cuando cambian unidades
- [[UnitSpinBox]] - Convierte valores de entrada/salida
- [[ScaleManager]] - Sistema de escala visual