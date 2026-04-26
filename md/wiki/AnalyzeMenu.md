---
name: AnalyzeMenu
description: Menú de análisis estructural (gravedad, modal, pushover y visualización de resultados)
type: reference
---

# AnalyzeMenu

Menú `QMenu` que agrupa todas las acciones de análisis y visualización de resultados.

**Clase:** `AnalyzeMenu(QMenu)`  
**Archivo:** `src/ui/menus/analyze_menu.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `_set_deformed_visibility(visible)` | Muestra/oculta la forma deformada en el viewport |
| `_clear_results()` | Limpia resultados del manager y refresca el viewport |
| `_show_diagram(type_)` | Activa el diagrama de fuerzas del tipo indicado (Momento, Cortante, Axial) |
| `run_gravity()` | Ejecuta `GravitySolver` vía `OpenSeesTranslator`; habilita visualización de deformada |
| `run_modal()` | Ejecuta análisis modal y muestra frecuencias |
| `show_pushover_dialog()` | Abre `PushoverDialog` (atajo F5) |
| `_show_curve_pushover()` | Abre `PushoverResultsWidget` con los resultados guardados en el manager |
| `_show_section_results()` | Abre `MomentCurvatureWidget` como tool window |
| `_show_fiber_strains()` | Abre `FiberStrainDialog` como tool window y lo conecta al `AnimationToolbar` via `connect_to_animation()` |

## Acciones del menú

| Acción | Función |
|-------|---------|
| Análisis Gravitacional | `run_gravity()` |
| Análisis Modal | `run_modal()` |
| Pushover (F5) | `show_pushover_dialog()` |
| Ver Curva de Capacidad | `_show_curve_pushover()` |
| Ver Resultados por Sección | `_show_section_results()` |
| Deformaciones de Fibras | `_show_fiber_strains()` |
| Limpiar Resultados | `_clear_results()` |

## Relaciones

```
AnalyzeMenu
├── OpenSeesTranslator ──► run_gravity(), run_modal()
├── PushoverDialog ──► show_pushover_dialog()
├── PushoverResultsWidget ──► _show_curve_pushover()
├── MomentCurvatureWidget ──► _show_section_results()
├── FiberStrainDialog ──► _show_fiber_strains()
└── MainWindow ──► lo instancia
```

## Relacionado Con

- [[PushoverDialog]] - Diálogo de configuración pushover
- [[PushoverResultsWidget]] - Curva de capacidad
- [[MomentCurvatureWidget]] - Resultados por sección
- [[FiberStrainDialog]] - Visualizador de fibras por paso
- [[OpenSeesTranslator]] - Ejecuta los análisis
- [[Menus]] - Índice de menús
