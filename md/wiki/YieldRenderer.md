---
name: YieldRenderer
description: Renderer de puntos de plastificación de fibras con gradiente de color amarillo→rojo
type: reference
---

# YieldRenderer

Renderiza en el viewport los puntos donde las fibras de los elementos han plastificado, con un gradiente de color que indica el nivel de plastificación (amarillo = inicio, rojo = avanzado).

**Clase:** `YieldRenderer`  
**Archivo:** `src/ui/visualizers/yield_renderer.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `redraw(step)` | Dibuja scatter de puntos plastificados en el paso indicado |
| `hide()` | Oculta el scatter |

## Mapa de colores

| Ratio fibras plastificadas | Color |
|--------------------------|-------|
| 0–33% | Amarillo |
| 33–66% | Naranja |
| 66–100% | Rojo |

## Relaciones

```
YieldRenderer
├── ProjectManager ──► yield_history[step]
└── StructureInteractor ──► llama redraw(step) junto con DeformationRenderer
```

## Relacionado Con

- [[Visualizers]] - Índice de visualizadores
- [[DeformationRenderer]] - Se dibuja superpuesto
- [[AnimationToolbar]] - Slider que pasa el `step`
- [[ProjectManager]] - `yield_history` con datos de plastificación
