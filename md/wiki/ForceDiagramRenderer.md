---
name: ForceDiagramRenderer
description: Renderer de diagramas de fuerzas internas (Momento, Cortante, Axial) con polígonos rellenos
type: reference
---

# ForceDiagramRenderer

Renderiza los diagramas de fuerzas internas como polígonos rellenos usando `MassivePolygonsItem` para máximo rendimiento.

**Archivos:** `src/ui/visualizers/force_diagram_renderer.py`

## Clases

### MassivePolygonsItem(pg.GraphicsObject)

Ítem pyqtgraph que dibuja miles de polígonos rellenos en una sola llamada QPainter, sin overhead por ítem.

| Función | Descripción |
|--------|-------------|
| `set_polygons(polygons, color)` | Reemplaza la lista de polígonos y fuerza repintado |
| `paint(p, *args)` | Dibuja todos los polígonos en una sola pasada con `p.drawPolygon()` |
| `boundingRect()` | Retorna el rectángulo envolvente de todos los polígonos |

### ForceDiagramRenderer

| Función | Descripción |
|--------|-------------|
| `show(type_)` | Activa el diagrama del tipo indicado y redibuja |
| `hide()` | Oculta todos los diagramas |
| `redraw()` | Recalcula y actualiza los polígonos |

## Tipos de diagrama

| Tipo | Color | Escala |
|-----|-------|--------|
| `moment` | Rojo semitransparente | `ScaleManager['moment']` |
| `shear` | Azul semitransparente | `ScaleManager['shear']` |
| `axial` | Verde semitransparente | `ScaleManager['axial']` |

## Relaciones

```
ForceDiagramRenderer
├── MassivePolygonsItem ──► renderizado eficiente
├── ProjectManager ──► resultados de análisis
├── ScaleManager ──► multiplicadores moment/shear/axial
└── StructureInteractor ──► llama show()/hide()
```

## Relacionado Con

- [[Visualizers]] - Índice de visualizadores
- [[AnalyzeMenu]] - `_show_diagram(type_)` lo activa
- [[ScaleManager]] - Escalas de los diagramas
