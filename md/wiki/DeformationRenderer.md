---
name: DeformationRenderer
description: Renderer de la forma deformada con interpolación cúbica de Hermite para vigas
type: reference
---

# DeformationRenderer

Renderiza la forma deformada del modelo con amplificación configurable. Para elementos tipo viga usa interpolación cúbica de Hermite (4 condiciones de contorno); para otros usa interpolación lineal.

**Clase:** `DeformationRenderer`  
**Archivo:** `src/ui/visualizers/deformation_renderer.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `redraw(step)` | Dibuja la deformada en el paso indicado usando `pushover_results` |
| `_compute_beam_curve(ni, nj, ui, vi, thi, uj, vj, thj, n_pts)` | Interpolación cúbica de Hermite para la línea elástica de la viga; retorna coordenadas x,y |
| `_on_hover(points, ev)` | Muestra tooltip con tag del elemento al pasar el cursor |

## Algoritmo Hermite

```
Shape functions:
H1 = 1 - 3ξ² + 2ξ³     H2 = ξ - 2ξ² + ξ³
H3 = 3ξ² - 2ξ³          H4 = -ξ² + ξ³
Transversal: v(ξ) = H1·vi + H2·θi·L + H3·vj + H4·θj·L
```

## Relaciones

```
DeformationRenderer
├── ProjectManager ──► pushover_results, get_all_elements()
├── ScaleManager ──► multiplicador 'deformation'
└── StructureInteractor ──► llama redraw(step)
```

## Relacionado Con

- [[Visualizers]] - Índice de visualizadores
- [[AnimationToolbar]] - Slider que pasa el `step`
- [[ScaleManager]] - Amplificación de la deformada
