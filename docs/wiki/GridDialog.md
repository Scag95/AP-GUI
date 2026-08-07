---
name: GridDialog
description: Diálogo modal para generar una grilla de pórtico (nodos + elementos) mediante FrameGenerator
type: reference
---

# GridDialog

Diálogo modal que recoge los parámetros geométricos de un pórtico regular (pisos, vanos, alturas, anchos, secciones) y los pasa a `FrameGenerator` para generar la malla.

**Clase:** `gridDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/grid_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `init_ui()` | Construye el formulario con campos geométricos y selección de secciones |
| `populate_sections()` | Rellena los combos de sección columnas/vigas con las secciones del manager |
| `get_data()` | Retorna dict con `stories`, `bays`, `story_height`, `bay_width`, `col_sec_tag`, `beam_sec_tag`, `add_base_beams`, `integration_points` |

## Campos del formulario

| Campo | Tipo | Default |
|------|------|---------|
| Número de pisos | `QSpinBox` | 1 |
| Número de vanos | `QSpinBox` | 1 |
| Altura de entrepiso | `UnitSpinBox LENGTH` | 3.0 m |
| Ancho de vano | `UnitSpinBox LENGTH` | 3.0 m |
| Generar vigas en base | `QCheckBox` | desactivado |
| Puntos de integración | `QSpinBox` (3-10) | 5 |
| Sección columnas | `QComboBox` | primera disponible |
| Sección vigas | `QComboBox` | primera disponible |

## Relaciones

```
GridDialog
├── ProjectManager ──► get_all_sections()
├── FrameGenerator ──► genera nodos y elementos con get_data()
├── UnitSpinBox ──► story_height, bay_width
└── DefineMenu ──► lo abre
```

## Relacionado Con

- [[FrameGenerator]] - Usa `get_data()` para construir la malla
- [[ProjectManager]] - Fuente de secciones
- [[DefineMenu]] - Menú que lo abre
- [[Sections]] - Secciones asignadas a columnas y vigas
