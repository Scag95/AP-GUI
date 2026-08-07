---
name: UnitSpinBox
description: QDoubleSpinBox con conversión automática de unidades según el sistema activo
type: reference
---

# UnitSpinBox

`QDoubleSpinBox` que almacena el valor en unidades canónicas (base) y muestra automáticamente el valor convertido al sistema de unidades activo. Se actualiza al cambiar el sistema global.

**Clase:** `UnitSpinBox(QDoubleSpinBox)`  
**Archivo:** `src/ui/widgets/unit_spinbox.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `_on_value_changed_internal(val)` | Cuando el usuario cambia el valor visual, recalcula y guarda `_base_value` |
| `_update_display()` | Actualiza sufijo y valor visual al cambiar de sistema de unidades |
| `get_value_base()` | Devuelve el valor en unidades canónicas (m, kN, Pa, etc.) |
| `set_value_base(base_value)` | Establece el valor usando unidades canónicas; actualiza el display sin emitir señales |
| `validate(text, pos)` | Delegado a `QDoubleSpinBox.validate()` |

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `unit_type` | `UnitType` | Tipo de unidad (LENGTH, FORCE, STRESS, etc.) |
| `_base_value` | `float` | Valor interno en unidades canónicas |

## Relaciones

```
UnitSpinBox
├── UnitManager ──► to_base(), from_base(), unitsChanged signal
└── UnitType ──► enum que identifica el tipo
```

Usado por: `PushoverDialog`, `GridDialog`, `SelfWeightDialog`, `GeometryDialog`, `ElementLoadsDialog`, `NodalLoadsDialog` y todos los formularios de secciones/materiales.

## Relacionado Con

- [[UnitManager]] - Fuente de conversión de unidades
- [[Widgets]] - Índice de widgets
