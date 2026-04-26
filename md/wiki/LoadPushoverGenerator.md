---
name: LoadPushoverGenerator
description: Fábrica que genera el vector de fuerzas laterales para el análisis pushover
type: reference
---

# LoadPushoverGenerator

Calcula la distribución de fuerzas laterales (modal, uniforme o patrón definido) usada durante el análisis pushover.

**Clase:** `LoadPushoverGenerator`  
**Archivo:** `src/analysis/solvers/load_generator.py`

## Clases

### LoadPatternResult (dataclass)

| Campo | Tipo | Descripción |
|------|------|-------------|
| `force_vector` | `dict[int, float]` | `{node_tag: force_x}` |
| `periods` | `list[float]` | Periodos fundamentales (si se calcularon) |

### LoadPushoverGenerator

| Función | Descripción |
|--------|-------------|
| `generate_pattern(pattern_type, n_modes)` | Punto de entrada; delega en `_generate_modal_pattern()` o `_generate_uniform_pattern()` |
| `_identify_master_nodes()` | Retorna `{y_coord: node_tag}` con el nodo de menor X por planta |
| `_generate_modal_pattern(master_nodes, n_modes)` | Ejecuta análisis modal en OpenSees y normaliza `F_i = M_i × Φ_i` |
| `_generate_uniform_pattern(master_nodes)` | Aplica fuerza uniforme proporcional a la masa de cada planta |

## Relaciones

```
LoadPushoverGenerator
├── ProjectManager ──► get_floor_data(), masas
├── ModelBuilder ──► referencia builder para ops.*
└── PushoverSolver ──► lo instancia y consume LoadPatternResult
```

## Relacionado Con

- [[Solvers]] - Índice de solvers
- [[PushoverSolver]] - Consumidor principal
- [[PushoverDialog]] - `combo_load_pattern_type` selecciona Modal/Uniforme/Patrón Definido
