---
name: FailureDetector
description: Detector de pérdida de capacidad estructural por planta durante el pushover
type: reference
---

# FailureDetector

Analiza la historia de desplazamientos y cortantes por planta para detectar formación de mecanismos (rigidez tangente < umbral) o deriva excesiva.

**Clase:** `FailureDetector`  
**Archivo:** `src/analysis/solvers/failure_detector.py`

## Clases

### FloorFailureState (dataclass)

| Campo | Tipo | Descripción |
|------|------|-------------|
| `y_level` | `float` | Coordenada Y de la planta |
| `cause` | `str` | Descripción del motivo del fallo |
| `k_ini` | `float` | Rigidez inicial de la planta |
| `k_tan` | `float` | Rigidez tangente en el paso de fallo |
| `current_drift` | `float` | Deriva en el paso de fallo |

### FailureDetector

| Atributo | Descripción |
|---------|-------------|
| `sensitivity` | Fracción de K_ini por debajo de la cual se considera mecanismo (default 0.001) |
| `max_drift` | Deriva relativa máxima permitida (opcional) |
| `cached_k_ini` | Caché de rigidez inicial por planta (se calcula una sola vez) |
| `reported_floors` | Conjunto de plantas ya impresas en el monitor (evita repetición) |

| Función | Descripción |
|--------|-------------|
| `analyze(results)` | Evalúa cada planta en `results["floors"]`; retorna `list[FloorFailureState]` |
| `_calculate_initial_stiffness(disps, shears)` | K_ini usando los primeros 20 pasos |
| `_calculate_tangent_stiffness(disps, shears)` | K_tan con pendiente de los últimos 2 puntos |

## Monitor de fallos

El monitor imprime el estado de **todas las plantas** únicamente cuando se detecta al menos un fallo **nuevo** (planta no incluida en `reported_floors`). Formato de salida:

```
[Fallo] Planta Y= 3.95 m | Paso:   278 | Deriva: 0.11524 m (2.92%) | K_tan/K_ini: -837534.21%
[OK]    Planta Y= 7.20 m | Paso:   278 | Deriva: 0.09995 m (3.08%) | K_tan/K_ini: 690392.23%
```

## Criterios de fallo

| Criterio | Condición |
|---------|-----------|
| Mecanismo | `k_tan < sensitivity × k_ini` |
| Deriva excesiva | `|disp|/H > max_drift` |

## Relaciones

```
FailureDetector
├── PushoverSolver ──► llama analyze() en cada iteración
└── PushoverDialog ──► spin_sensitivity y spin_max_drift configuran los parámetros
```

## Relacionado Con

- [[Solvers]] - Índice de solvers
- [[PushoverSolver]] - Solver que lo usa
- [[PushoverDialog]] - Parámetros configurables desde UI
