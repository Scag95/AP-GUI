---
name: MomentCurvatureWidget
description: Widget para visualizar la curva momento-curvatura por sección a partir de datos de pushover
type: reference
---

# MomentCurvatureWidget

Widget de resultados que muestra la curva M-φ (o P/V vs φ) por sección de integración de un elemento, leyendo los archivos CSV generados durante el análisis pushover.

**Clase:** `MomentCurvatureWidget(QWidget)`  
**Archivo:** `src/ui/dialogs/moment_curvature_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `init_ui()` | Construye panel izquierdo (controles) y derecho (`pg.PlotWidget` + slider) |
| `load_available_elements()` | Escanea `pushover_data/` buscando archivos de sección; rellena `element_combo` |
| `_on_element_changed()` | Al cambiar elemento, repobla `section_list` con checkboxes por sección |
| `_on_slider_changed(value)` | Actualiza `current_step_val` y llama `update_plot()` |
| `load_element_data(tag)` | Carga los CSV del elemento y actualiza la lista de secciones disponibles |
| `update_plot()` | Dibuja las curvas seleccionadas en `pg.PlotWidget`, hasta el paso del slider |

## Controles

| Control | Descripción |
|--------|-------------|
| `element_combo` | Selector de elemento |
| `y_axis_combo` | Variable eje Y: Momento Mz / Fuerza Axial P / Cortante Vy |
| `section_list` | Lista con checkboxes por sección de integración |
| `slider_step` | Anima la curva hasta un paso específico |
| `lbl_plot_info` | Información del paso actual |

## Relaciones

```
MomentCurvatureWidget
├── ProjectManager ──► instance()
├── pyqtgraph ──► pg.PlotWidget para la curva
├── pushover_data/ ──► CSVs de sección generados por PushoverSolver
└── ToolsMenu ──► lo abre como tool window
```

## Relacionado Con

- [[Solvers]] - `PushoverSolver` genera los archivos CSV leídos
- [[ToolsMenu]] - Menú que lo abre
- [[PushoverResultsWidget]] - Widget hermano de resultados globales
