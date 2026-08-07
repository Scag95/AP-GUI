---
name: GravitySolver
description: Solver para análisis gravitacional estático en OpenSees
type: reference
---

# GravitySolver

Encapsula la secuencia de comandos OpenSeesPy necesaria para ejecutar un análisis gravitacional (cargas de peso propio y sobrecargas estáticas).

**Clase:** `GravitySolver`  
**Archivo:** `src/analysis/solvers/gravity_solver.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `run()` | Configura y ejecuta el análisis gravitacional (`ops.analyze`) |
| `get_results()` | Retorna desplazamientos, reacciones y fuerzas de sección por elemento |

## Captura de fuerzas de sección (`get_results`)

Para cada elemento con `integration_points`, extrae P, M y V por punto de integración usando:

- `eleResponse(tag, 'section', i, 'force')` → P y M (y V si la sección tiene DOF Vy)
- `eleResponse(tag, 'localForce')` → fuerzas en los extremos del elemento

Cuando la sección **no tiene DOF Vy** (`len(sec_forces) == 2`), el cortante se reconstruye interpolando linealmente entre los extremos del elemento:

```python
loc_rel = loc / L          # normalizado [0, 1]
v_val = V_i*(1-loc_rel) + (-V_j)*loc_rel
```

donde `L` es la longitud del elemento calculada desde las coordenadas de sus nodos, y `loc` es la posición absoluta devuelta por `sectionLocation` (en las mismas unidades que las coordenadas).

## Relaciones

```
GravitySolver
├── ModelBuilder ──► builder pasado en __init__
├── OpenSeesTranslator ──► lo instancia y llama run()
└── AnalyzeMenu ──► dispara run_gravity()
```

## Relacionado Con

- [[Solvers]] - Índice de solvers
- [[OpenSeesTranslator]] - Orquestador
- [[AnalyzeMenu]] - Acción que lo dispara
