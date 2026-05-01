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
| `run_gravity()` | Ejecuta `GravitySolver` vía `OpenSeesTranslator`; habilita visualización de deformada |
| `run_modal()` | Ejecuta análisis modal y muestra frecuencias |
| `show_pushover_dialog()` | Abre `PushoverDialog` (atajo F5) |

## Acciones del menú

| Acción | Función |
|-------|---------|
| Análisis Gravitacional | `run_gravity()` |
| Análisis Modal | `run_modal()` |
| Pushover (F5) | `show_pushover_dialog()` |

## Nota

Las acciones de visualización de resultados (Curva Pushover, Diagramas, Moment-Curvature, Fiber Strains) se encuentran ahora en el menú [[ResultsMenu]]. |

## Relaciones

```
AnalyzeMenu
├── OpenSeesTranslator ──► run_gravity(), run_modal()
├── PushoverDialog ──► show_pushover_dialog()
├── ResultsMenu ──► Contiene acciones de visualización de resultados
└── MainWindow ──► lo instancia
```

## Relacionado Con

- [[PushoverDialog]] - Diálogo de configuración pushover
- [[ResultsMenu]] - Menú de visualización de resultados
- [[OpenSeesTranslator]] - Ejecuta los análisis
- [[Menus]] - Índice de menús
