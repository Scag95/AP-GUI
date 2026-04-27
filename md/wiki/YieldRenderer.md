---
name: YieldRenderer
description: Renderiza puntos de fluencia y cruces de colapso en la forma deformada, coloreados por estado límite EC8
type: reference
---

# YieldRenderer

Renderiza en el viewport la ubicación de secciones que han alcanzado estados límite EC8 (DL/SL/NC) durante el pushover. Usa tres `ScatterPlotItem` de pyqtgraph con brush fijo (uno por color) para máximo rendimiento.

**Clase:** `YieldRenderer`  
**Archivo:** `src/ui/visualizers/yield_renderer.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `clear(plot_widget)` | Elimina del plot los ScatterPlotItems activos |
| `reset_limit_state_history()` | Limpia `_max_limit_state`, `_last_step` y `_node_map` — llamar al inicio de cada análisis |
| `clear_crosses(plot_widget)` | Elimina las líneas de cruces de San Andrés |
| `_accumulate_limit_states(step_yield_data)` | Actualiza `_max_limit_state` con el peor estado de un paso (sin dibujar) |
| `draw_yield_state(plot_widget, manager, step_yield_data, step_displacements, step_index)` | Gestiona scrubbing inverso, acumula estados y dibuja puntos de fluencia sobre la deformada |
| `_flush_scatter(plot_widget, xs, ys)` | Actualiza los 3 ScatterPlotItems con arrays numpy; añade/elimina items del plot según haya puntos |
| `draw_frozen_floors(plot_widget, frozen_floors, frozen_columns, step_displacements, scale_factor, manager)` | Dibuja cruces de San Andrés (colapso de piso) |

## Estados límite y colores

| Estado | Condición (FiberSection) | Condición (AggregatorSection) | Color |
|--------|--------------------------|-------------------------------|-------|
| DL — Daño Limitado | `abs(ε) ≥ εy` (acero) | `κ ≥ κy` | Amarillo (220,180,0) |
| SL — Seguridad de Vida | `abs(ε) ≥ 0.75·εcu` (hormigón) | `κ ≥ κsl` | Naranja (230,100,0) |
| NC — Near Collapse | `abs(ε) ≥ 1.25·εcu` (hormigón) | `κ ≥ κnc` | Rojo (210,0,0) |

El color de un punto es siempre el **peor estado acumulado** de la sección desde el paso 0 hasta el paso actual.

## Datos de entrada: `step_yield_data`

```python
{
  ele_tag: {
    sec_num: [
      {"ratio": float,          # ε/umbral o κ/κy — solo se pinta si >= 1.0
       "loc": float,            # posición a lo largo del elemento (m)
       "limit_state": "DL"|"SL"|"NC",
       "fiber_idx": int}        # solo FiberSection
    ]
  }
}
```

Tanto `FiberSection` como `AggregatorSection` producen una **lista de dicts** (el bug de retornar dict suelto fue corregido en `_ls_yield_aggregator`).

## Diseño de rendimiento

- **3 ScatterPlotItem permanentes** con brush fijo (uno por LS). Brush creado una sola vez en `__init__`, no por punto.
- **`setData(x=arr, y=arr)`** con arrays numpy — procesado en C++ sin loop Python.
- **`addItem`/`removeItem` mínimos** — solo cuando el estado del LS cambia (set `_in_scene`).
- **`_node_map` cacheado** durante la animación (se reconstruye solo si está vacío).
- **Scrubbing inverso**: si `step_index ≤ _last_step`, limpia `_max_limit_state` y reprocesa pasos 0..N-1 desde `manager.yield_history` antes de dibujar.

## Relaciones

```
YieldRenderer
├── ProjectManager ──► yield_history, get_all_nodes(), get_element()
├── ScaleManager   ──► get_scale('deformation')
└── StructureInteractor ──► instancia y llama draw_yield_state / draw_frozen_floors
```

## Relacionado Con

- [[Visualizers]] - Índice de visualizadores
- [[StructureInteractor]] - Caller principal
- [[AnimationToolbar]] - Pasa step_index al slider
- [[ProjectManager]] - Fuente de yield_history y nodos
