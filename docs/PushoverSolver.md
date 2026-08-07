---
name: PushoverSolver
description: Solver para análisis pushover monotónico y adaptativo en OpenSees
type: reference
---

# PushoverSolver

Ejecuta el análisis pushover paso a paso, registra desplazamientos y cortantes por piso, y vuelca resultados de sección a archivos CSV en `pushover_data/`.

**Clase:** `PushoverSolver`  
**Archivo:** `src/analysis/solvers/pushover_solver.py`

## Funciones principales

| Función | Descripción |
|--------|-------------|
| `run_pushover(...)` | Pushover monotónico paso a paso; acepta `progress_callback(step, total)` |
| `run_adaptative_pushover(...)` | Pushover adaptativo por rondas; acepta `progress_callback(step, total, round_idx, total_rounds)` |
| `_get_all_element_forces()` | Captura P, M, V por punto de integración en el paso actual |
| `_capture_step_state(...)` | Acumula desplazamientos, cortantes de planta y fuerzas de sección |
| `_merge_results(...)` | Fusiona resultados de una ronda al histórico consolidado |
| `run_modal_analysis(n_modes)` | Eigenanálisis modal; retorna lista de períodos |

## Barra de progreso (`progress_callback`)

`run_pushover` llama al callback en cada paso:
```python
progress_callback(i, n_steps)
```

`run_adaptative_pushover` propaga el callback por ronda, pasando además el índice de ronda:
```python
progress_callback(step_in_round, total_in_round, round_idx, MAX_ROUND)
```
El análisis adaptativo para automáticamente cuando **todos los pisos estructurales** están congelados (`frozen_floors >= structural_floors`).

## Interpolación de cortante

Cuando `eleResponse(tag, 'section', i, 'force')` retorna solo 2 componentes (sin DOF Vy), el cortante se reconstruye desde `localForce`:
```python
loc_rel = loc / L
v_val = V_i*(1-loc_rel) + (-V_j)*loc_rel
```
`loc` es posición absoluta del punto de integración (metros); se normaliza por la longitud `L` del elemento.

## Relaciones

```
PushoverSolver
├── ModelBuilder ──► builder pasado en __init__
├── PushoverConfigurator ──► setup_static_analysis(), run_static_step_with_fallback()
├── LoadPushoverGenerator ──► genera el vector de fuerzas laterales
├── FailureDetector ──► detecta fallos de planta (modo adaptativo)
├── OpenSeesTranslator ──► lo instancia y ejecuta
└── MomentCurvatureWidget ──► lee los CSVs generados
```

## Relacionado Con

- [[Solvers]] - Índice de solvers
- [[PushoverConfigurator]] - Configura el análisis estático
- [[LoadPushoverGenerator]] - Vector de fuerzas
- [[FailureDetector]] - Detección de mecanismo
- [[MomentCurvatureWidget]] - Consume los CSVs generados
- [[PushoverResultsWidget]] - Consume el dict de resultados
