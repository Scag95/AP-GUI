---
name: PushoverResultsWidget
description: Widget para visualizar la curva de capacidad pushover (cortante basal vs desplazamiento)
type: reference
---

# PushoverResultsWidget

Widget de resultados que muestra la curva de capacidad global (Base Shear vs Roof Drift) y por piso, con slider de pasos y marcadores de estados límite (DL/SL/NC).

**Clase:** `PushoverResultsWidget(QWidget)`  
**Archivo:** `src/ui/dialogs/pushover_result_dialog.py`

## Constructor

```python
PushoverResultsWidget(results, initial_load_viz_state=False, parent=None)
```

`results` es el diccionario devuelto por `run_pushover_analysis()` / `run_adaptive_pushover()`.

## Funciones

| Función | Descripción |
|--------|-------------|
| `_on_toggle_loads(state)` | Activa/desactiva la visualización de fuerzas pushover en la ventana principal |
| `_on_slider_changed(value)` | Actualiza `current_step_val` y llama `update_plot()` |
| `update_plot()` | Dibuja en `pg.PlotWidget` las curvas seleccionadas hasta el paso del slider |
| `_draw_limit_state_markers(curves_data, slider_limit, um)` | Dibuja líneas verticales coloreadas para estados límite DL/SL/NC |

## Controles

| Control | Descripción |
|--------|-------------|
| `list_curves` | Lista con checkboxes: Global + un ítem por piso (Y= …) |
| `chk_toggle_loads` | Muestra/oculta fuerzas pushover en viewport 3D |
| `plot_widget` | `pg.PlotWidget` con curva de capacidad |
| `slider_step` | Anima la curva paso a paso |
| `lbl_step` | Etiqueta del paso actual |
| `lbl_plot_info` | Info de desplazamiento y cortante en el paso |

## Estados límite

Marcadores dibujados por `_draw_limit_state_markers()`:

| Estado | Color |
|-------|-------|
| DL (Daño Limitado) | Verde |
| SL (Seguridad de Vida) | Naranja |
| NC (Near Collapse) | Rojo |

## Relaciones

```
PushoverResultsWidget
├── ProjectManager ──► instance()
├── pyqtgraph ──► pg.PlotWidget
├── PushoverDialog ──► lo crea y pasa results
├── MainWindow ──► add_tool_window(), set_pushover_loads_visible()
└── Solvers ──► results dict con floors / global / limit_states
```

## Relacionado Con

- [[PushoverDialog]] - Lo instancia tras el análisis
- [[Solvers]] - Fuente del dict `results`
- [[MainWindow]] - Muestra el widget como tool window
- [[MomentCurvatureWidget]] - Widget hermano de resultados por sección
