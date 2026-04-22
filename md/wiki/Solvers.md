# Solvers

Directorio `src/analysis/solvers/` que contiene los solvers especializados para análisis.

## Clases

### GravitySolver

Ejecuta análisis de gravedad básico con Newton-Raphson.

```python
class GravitySolver:
```

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `__init__(builder)` | Recibe ModelBuilder | None |
| `run()` | Ejecuta análisis estático | bool |
| `get_results()` | Extrae desplazamientos, reacciones, fuerzas | dict |

### PushoverSolver

Orquestador principal del análisis pushover.

```python
class PushoverSolver:
```

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `__init__(builder)` | Recibe ModelBuilder | None |
| `run_pushover()` | Pushover monotónico estándar | dict |
| `run_adaptative_pushover()` | Pushover adaptativo con freeze de pisos | dict |
| `run_modal_analysis()` | Análisis de autovalores | list |
| `_apply_load_pattern()` | Aplica vector de fuerzas | None |
| `_capture_step_state()` | Captura estado del modelo | None |
| `_get_base_shear()` | Calcula cortante basal | float |
| `_setup_recorders()` | Configura recorders de OpenSees | None |
| `_initialize_supports()` | Inicializa apoyos activos | None |
| `_initialize_results_structure()` | Prepara diccionario de resultados | dict |
| `_get_all_node_displacements()` | Captura desplazamientos | dict |
| `_get_all_element_forces()` | Captura fuerzas | dict |
| `_capture_floor_data()` | Calcula drift y cortante por planta | None |
| `_merge_results()` | Une resultados de rondas | None |
| `_get_deformed_floor_state()` | Extrae estado deformado | list |

### FailureDetector

Detecta mecanismos de colapso analizando drifts y cambios de velocidad de rigidez.

```python
class FailureDetector:
    sensitivity: float     # Factor para rigidez tangente/inicial (default 0.001)
    max_drift: float      # Deriva máxima (%) para declarar colapso
    cached_k_ini: dict   # Rigidez inicial por planta
```

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `__init__(sensitivity, max_drift)` | Configura umbrales | None |
| `analyze()` | Evalúa cada planta buscando mecanismos | list |

### FloorFailureState

```python
@dataclass
class FloorFailureState:
    y_level: float      # Cota Y de la planta
    cause: str         # Causa del fallo
    k_ini: float      # Rigidez inicial
    k_tan: float     # Rigidez tangente actual
    current_drift: float  # Deriva actual
```

### SteelYieldDetector

Detecta fluencia en secciones de acero monitoreando strain en fibras.

**Clase:** `SteelYieldDetector`

**Atributos:**

| Atributo | Descripción |
|----------|-------------|
| `_baseline` | Set de (ele_tag, sec_num) pre-fluidos por gravedad |

**Funciones:**

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `reset()` | Limpia baseline | None |
| `capture_baseline()` | Registra secciones ya fluidas por gravedad | None |
| `_get_section_tag()` | Obtiene section_tag según tipo de elemento | int |
| `_get_loc()` | Obtiene posición de sección | float |
| `_get_fiber_material_tags()` | Lista mat_tags ordenados como OpenSees | list |
| `_capture_fiber_section()` | Captura via fiberData de FiberSection | dict |
| `_capture_aggregator_section()` | Captura via deformation+κ de AggregatorSection | dict |
| `_capture_raw()` | Captura sin filtrar | dict |
| `capture_step()` | Captura excluyendo baseline | dict |

**Retorna capture_step():**
```python
{ ele_tag: { sec_num: { "ratio": float, "strain": float, "loc": float } } }
# ratio > 1 indica fluencia
```

**Relacionado:** [[PushoverSolver]], [[ScaleManager]]

### LoadPushoverGenerator

Genera vectores de carga lateral.

```python
class LoadPushoverGenerator:
```

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `generate_pattern()` | Genera vector según tipo | LoadPatternResult |
| `_identify_master_nodes()` | Identifica nodos de control por planta | dict |
| `_generate_modal_pattern()` | Patrón basado en modo 1 | LoadPatternResult |
| `_generate_uniform_pattern()` | Patrón uniforme | LoadPatternResult |

### LoadPatternResult

```python
@dataclass
class LoadPatternResult:
    force_vector: Dict[int, float]  # {node_tag: force_x}
    periods: List[float]            # Períodos fundamentales
```

### PushoverConfigurator

Configura el sistema de ecuaciones y algoritmos de OpenSees.

```python
class PushoverConfigurator:
```

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `setup_static_analysis()` | Configura análisis estático | None |
| `run_static_step_with_fallback()` | Ejecuta un paso | int |

## Flujo Pushover Adaptativo

```
PushoverSolver.run_adaptative_pushover()
    │
    ├─► _initialize_supports()
    ├─► _setup_recorders()
    ├─► LoadPushoverGenerator.generate_pattern()
    │
    └─► for ronda in MAX_ROUND:
            ├─► run_pushover()
            │   ├─► _apply_load_pattern()
            │   ├─► PushoverConfigurator.setup_static_analysis()
            │   ├─► for step in steps:
            │   │   ├─► PushoverConfigurator.run_static_step_with_fallback()
            │   │   ├─► _capture_step_state()
            │   │   └─► SteelYieldDetector.capture_step()
            │   └─► FailureDetector.analyze()
            ├─► _merge_results()
            └─► if nuevos_fallos:
                    └─► ModelBuilder.freeze_floor()
```

## Relaciones

```
Solvers
├── OpenSeesTranslator ──► Los instancia
├── ModelBuilder ──► Acceden al builder
├── ProjectManager ──► Almacenan/leen resultados
│   ├─ gravity_results
│   ├─ pushover_results
│   ├─ yield_history
│   └─ pushover_loads
├── AnimationToolbar ──► Consume resultados
└── LoadRenderer ──► Dibuja pushover_loads
```

## Relacionado Con

- [[OpenSeesTranslator]] - Fachada que usa los solvers
- [[ModelBuilder]] - Construye el modelo OpenSees
- [[ProjectManager]] - Almacena resultados
- [[PushoverDialog]] - UI para configurar pushover
- [[AnimationToolbar]] - Consume resultados