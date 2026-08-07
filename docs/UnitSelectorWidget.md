---
name: UnitSelectorWidget
description: QComboBox para seleccionar el sistema de unidades mediante presets
type: reference
---

# UnitSelectorWidget

`QComboBox` embebido en la barra de estado que aplica presets de sistema de unidades completo al `UnitManager`.

**Clase:** `UnitSelectorWidget(QComboBox)`  
**Archivo:** `src/ui/widgets/unit_selector.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `_apply_preset(index)` | Al cambiar el índice, aplica el mapa `{UnitType: unit_name}` al `UnitManager` en bloque (bloquea señales para evitar múltiples refrescos) |

## Presets disponibles

| Label | Force | Length | Stress |
|------|-------|--------|--------|
| kN, m | kN | m | MPa |
| N, mm | N | mm | MPa |
| Ton, m | Ton | m | kg/cm² |
| kips, ft | kips | ft | ksi |

## Relaciones

```
UnitSelectorWidget
├── UnitManager ──► set_unit(), unitsChanged.emit()
└── MainWindow ──► lo añade a la status bar
```

## Relacionado Con

- [[UnitManager]] - Sistema de unidades global
- [[UnitSpinBox]] - Se actualiza al cambiar el preset
- [[MainWindow]] - Lo aloja en la barra de estado
- [[Widgets]] - Índice de widgets
