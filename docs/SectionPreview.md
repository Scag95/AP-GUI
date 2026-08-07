---
name: SectionPreview
description: Widget de previsualización gráfica de secciones transversales de fibra
type: reference
---

# SectionPreview

Widget basado en `pg.PlotWidget` que renderiza en tiempo real la geometría de una `FiberSection` (patches rectangulares y layers de refuerzo).

**Clase:** `SectionPreview(pg.PlotWidget)`  
**Archivo:** `src/ui/widgets/section_preview.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `_setup_ui()` | Configura aspecto del PlotWidget (fondo, ejes, razón de aspecto bloqueada) |
| `plot_section(section)` | Limpia el plot y dibuja patches como `pg.QtGui.QGraphicsRectItem` y layers como `pg.ScatterPlotItem` |

## Elementos gráficos

| Elemento | Representación |
|---------|---------------|
| Patch cobertura | Rectángulo gris claro |
| Patch núcleo | Rectángulo azul oscuro |
| Layer refuerzo | Scatter de puntos negros |

## Relaciones

```
SectionPreview
├── SectionDialog ──► llama plot_section() al cambiar parámetros
├── SectionForms ──► _build_section_from_form() para preview temporal
└── Sections ──► FiberSection para renderizar
```

## Relacionado Con

- [[SectionDialog]] - Contiene este widget
- [[SectionForms]] - Genera la sección temporal previsualizada
- [[Sections]] - `FiberSection` renderizada
- [[Widgets]] - Índice de widgets
