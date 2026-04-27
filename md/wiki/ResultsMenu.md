# ResultsMenu

Menú `QMenu` dedicado a la visualización de resultados del análisis estructural.

**Clase:** `ResultsMenu(QMenu)`  
**Archivo:** `src/ui/menus/results_menu.py`

## Propósito

Agrupa todas las acciones de visualización de resultados que antes estaban en el submenú de `AnalyzeMenu`. Se sitúa entre los menús **Analizar** y **Ver** en la barra de menús.

## Acciones del menú

| Acción | Función |
|-------|---------|
| Deformada | `_set_deformed_visibility(True)` |
| Momentos (M) | `_show_diagram("M")` |
| Cortantes (V) | `_show_diagram("V")` |
| Axiales (P) | `_show_diagram("P")` |
| Curva Pushover | `_show_curve_pushover()` |
| Análisis de Sección (M-φ) | `_show_section_results()` |
| Deformaciones de Fibras | `_show_fiber_strains()` |
| Ocultar Resultados | `_clear_results()` |

## Funciones

| Función | Descripción |
|--------|-------------|
| `_set_deformed_visibility(visible)` | Muestra/oculta la forma deformada |
| `_show_diagram(type_)` | Activa diagrama de fuerzas (M/V/P) |
| `_show_curve_pushover()` | Abre `PushoverResultsWidget` con curva de capacidad |
| `_show_section_results()` | Abre `MomentCurvatureWidget` |
| `_show_fiber_strains()` | Abre `FiberStrainDialog` y conecta al `AnimationToolbar` |
| `_clear_results()` | Oculta todos los resultados en todos los viewports |

## Relaciones

```
ResultsMenu
├── PushoverResultsWidget ──► _show_curve_pushover()
├── MomentCurvatureWidget ──► _show_section_results()
├── FiberStrainDialog ──► _show_fiber_strains() + AnimationToolbar
├── StructureInteractor ──► Viz widget para diagramas y deformada
└── MainWindow ──► Lo instancia entre Analizar y Ver
```

## Relacionado Con

- [[AnalyzeMenu]] - Menú de análisis (sin submenú de resultados)
- [[PushoverResultsWidget]] - Curva de capacidad
- [[MomentCurvatureWidget]] - Resultados por sección
- [[FiberStrainDialog]] - Visualizador de fibras
- [[MainWindow]] - Lo posiciona entre Analizar y Ver
- [[Menus]] - Índice de menús