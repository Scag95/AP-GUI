---
name: PushoverConfigurator
description: Configura el análisis estático no lineal en OpenSees con estrategia de fallback
type: reference
---

# PushoverConfigurator

Encapsula la configuración del análisis estático incremental (`ops.integrator`, `ops.algorithm`, `ops.analysis`) y la lógica de fallback cuando un paso no converge.

**Clase:** `PushoverConfigurator`  
**Archivo:** `src/analysis/solvers/pushover_configurator.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `setup_static_analysis(control_node_tag, incr_disp)` | Configura integrador Displacement Control, algoritmo Newton y análisis Static |
| `run_static_step_with_fallback()` | Intenta `ops.analyze(1)`; si falla, reduce el paso y reintenta con algoritmos alternativos (KrylovNewton, etc.) |

## Relaciones

```
PushoverConfigurator
├── ModelBuilder ──► referencia builder
└── PushoverSolver ──► lo usa paso a paso
```

## Relacionado Con

- [[Solvers]] - Índice de solvers
- [[PushoverSolver]] - Orquestador que lo usa
