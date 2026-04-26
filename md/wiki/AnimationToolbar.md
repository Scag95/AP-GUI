---
name: AnimationToolbar
description: Barra de herramientas para animar la deformada pushover paso a paso
type: reference
---

# AnimationToolbar

`QToolBar` que aparece al completar un análisis pushover. Permite navegar por los pasos de la deformada con un slider sincronizado con el viewport.

**Clase:** `AnimationToolbar(QToolBar)`  
**Archivo:** `src/ui/widgets/animation_toolbar.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `load_pushover_results()` | Lee `pushover_results` del manager; configura el rango del slider y muestra la toolbar |
| `_on_slider_changed(value)` | Al mover el slider, actualiza la deformada en el viewport al paso correspondiente; si `chk_sync` está activo, sincroniza también el slider del `PushoverResultsWidget` |

## Controles

| Control | Descripción |
|--------|-------------|
| `slider` | `QSlider` horizontal con rango 0..N_pasos |
| `lbl_step` | Etiqueta que muestra el paso actual |
| `chk_sync` | Checkbox para sincronizar con el `PushoverResultsWidget` |

## Relaciones

```
AnimationToolbar
├── ProjectManager ──► pushover_results, yield_history
├── StructureInteractor ──► draw_deformed_shape(step)
├── PushoverResultsWidget ──► sincroniza slider (chk_sync)
└── MainWindow ──► toggle_animation_toolbar()
```

## Relacionado Con

- [[ProjectManager]] - Fuente de `pushover_results` y `yield_history`
- [[PushoverResultsWidget]] - Widget sincronizable
- [[MainWindow]] - Gestiona visibilidad de la toolbar
- [[Widgets]] - Índice de widgets
