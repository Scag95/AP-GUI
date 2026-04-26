---
name: LoadRenderer
description: Renderer vectorizado de cargas nodales y distribuidas en el viewport
type: reference
---

# LoadRenderer

Dibuja las cargas del modelo como flechas vectorizadas usando `pg.PlotDataItem`. Utiliza `numpy` para generar todos los segmentos de una sola vez.

**Clase:** `LoadRenderer`  
**Archivo:** `src/ui/visualizers/load_renderer.py`

## Funciones internas

| Función | Descripción |
|--------|-------------|
| `_draw_nodal_load(load, node, scale)` | Genera segmentos de flecha para `NodalLoad` (Fx, Fy) |
| `_draw_element_load(load, elem, scale)` | Genera segmentos de flecha distribuidos a lo largo del elemento para `ElementLoad` (wy) |

## Relaciones

```
LoadRenderer
├── ProjectManager ──► get_all_patterns(), get_node(), get_element()
├── ScaleManager ──► multiplicador 'load'
└── StructureInteractor ──► llama redraw()
```

## Relacionado Con

- [[Visualizers]] - Índice de visualizadores
- [[NodalLoad]] - Carga representada
- [[ElementLoad]] - Carga representada
- [[ScaleManager]] - Escala de cargas
- [[StructureInteractor]] - Orquestador
