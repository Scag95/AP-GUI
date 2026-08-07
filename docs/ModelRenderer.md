---
name: ModelRenderer
description: Renderer del modelo estructural no deformado (nodos, elementos, condiciones de borde)
type: reference
---

# ModelRenderer

Dibuja el modelo estructural en su posición original: elementos como líneas, nodos como puntos, y las condiciones de borde (empotramientos, apoyos) como símbolos geométricos.

**Clase:** `ModelRenderer`  
**Archivo:** `src/ui/visualizers/model_renderer.py`

## Responsabilidades

- Renderiza todos los elementos (`pg.PlotDataItem`) con colores por tipo
- Dibuja nodos como `pg.ScatterPlotItem`
- Dibuja símbolos de restricción (triángulo, línea base, empotrado)

## Símbolos de restricción

| Fixity [UX,UY,RZ] | Símbolo |
|------------------|---------|
| [1,1,1] | Cuadrado (empotrado) |
| [0,1,1] | Triángulo + base |
| [0,1,0] | Triángulo (apoyo simple) |
| [1,0,0] | Rodillo horizontal |

## Relaciones

```
ModelRenderer
├── ProjectManager ──► get_all_nodes(), get_all_elements()
├── ScaleManager ──► node_size
└── StructureInteractor ──► llama redraw()
```

## Relacionado Con

- [[Visualizers]] - Índice de visualizadores
- [[StructureInteractor]] - Orquestador de renderizado
- [[ScaleManager]] - Escala de nodos
