# ProjectManager

Gestor central de datos de la aplicación. Singleton + QObject.

## Clase
`ProjectManager`

## Propósito
Almacena todos los datos del modelo estructural y emite señales de cambio a la UI.

## Singleton
```python
ProjectManager.instance()
```

## Estructura de Datos

```python
ProjectManager
├── material{}             # tag → Material
├── section{}             # tag → Section
├── node{}               # tag → Node
├── element{}             # tag → Element
├── patterns{}            # tag → LoadPattern
├── gravity_results       # dict o None
├── pushover_results      # dict o None
├── yield_history         # list — estado de fluencia por paso [{ele_tag:{sec_num:{...}}}]
├── floor_limit_states    # dict — {y_level: {DL, SL, NC}} primer roof_disp de cada LS
├── pushover_loads        # list
├── _ls_pre_existing      # set  — (ele_tag, sec_num, ls) activos bajo gravedad
├── _ls_elem_floor_map    # dict — ele_tag → y_level
└── _floors_cache         # dict (privado)
```

## Señales

```python
dataChanged = pyqtSignal()  # Emitido cuando los datos cambian
```

## Funciones por Categoría

### Materiales

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `add_material()` | Agrega material | None |
| `get_material()` | Obtiene material por tag | Material |
| `get_all_materials()` | Lista todos | list |
| `delete_material()` | Elimina material | None |
| `get_next_material_tag()` | Próximo tag disponible | int |

### Secciones

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `add_section()` | Agrega sección | None |
| `get_section()` | Obtiene sección por tag | Section |
| `get_all_sections()` | Lista todas | list |
| `delete_section()` | Elimina sección | None |
| `get_next_section_tag()` | Próximo tag disponible | int |

### Nodos

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `add_node()` | Agrega nodo y marca topología sucia | None |
| `get_node()` | Obtiene nodo por tag | Node |
| `get_all_nodes()` | Lista todos | list |
| `delete_node()` | Elimina nodo | None |
| `get_next_node_tag()` | Próximo tag disponible | int |

### Elementos

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `add_element()` | Agrega elemento y marca topología sucia | None |
| `get_element()` | Obtiene elemento por tag | Element |
| `get_all_elements()` | Lista todos | list |
| `delete_element()` | Elimina elemento | None |
| `get_next_element_tag()` | Próximo tag disponible | int |

### Pisos (Floor Topology)

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `get_floor_data()` | Obtiene datos de pisos (con caché) | dict |
| `get_floor_masses()` | Calcula masas por planta | dict |
| `mark_topology_dirty()` | Invalida caché de pisos | None |

### Patrones de Carga

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `add_pattern()` | Agrega patrón | None |
| `get_pattern()` | Obtiene patrón por tag | LoadPattern |
| `get_all_patterns()` | Lista todos | list |
| `delete_pattern()` | Elimina patrón | None |
| `get_next_pattern_tag()` | Próximo tag disponible | int |

### Cargas

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `add_load()` | Inserta carga en patrón | None |
| `get_load()` | Busca carga por tag | Load |
| `get_all_loads()` | Lista todas las cargas | list |
| `delete_load()` | Elimina carga | None |
| `get_next_load_tag()` | Próximo tag disponible | int |

### Persistencia

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `save_project()` | Guarda proyecto a JSON | bool |
| `load_project()` | Carga proyecto desde JSON | bool |
| `new_project()` | Reinicia estado completo | None |

### Detección de Estados Límite EC8

API pública — llamada por `PushoverSolver`:

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `reset_limit_states()` | Reinicia mapas y `floor_limit_states`. Llamar antes de cada análisis | None |
| `capture_limit_state_baseline()` | Registra estados ya activos bajo gravedad | None |
| `capture_limit_state_step(roof_disp)` | Una llamada por paso: actualiza `yield_history` y `floor_limit_states` | None |
| `get_floor_limit_states()` | Retorna copia de `floor_limit_states` | dict |

Helpers privados (prefijo `_ls_`):

| Función | Propósito |
|--------|-----------|
| `_ls_build_floor_map()` | Construye mapa ele→planta |
| `_ls_get_sec_tag()` | Section tag según tipo de elemento |
| `_ls_get_loc()` | Posición normalizada de la sección |
| `_ls_fiber_mat_tags()` | Lista mat_tags en orden OpenSees |
| `_ls_get_mz_mat()` | Material Mz de una AggregatorSection |
| `_ls_yield_fiber()` | Dato de fluencia de FiberSection (para yield_history) |
| `_ls_yield_aggregator()` | Dato de fluencia de AggregatorSection con signo correcto |
| `_ls_check_fiber()` | Actualiza floor_result con umbrales Steel01/Concrete01 |
| `_ls_check_aggregator()` | Actualiza floor_result con umbrales Hysteretic/HystereticSM |

**Constantes de clase:**
```python
EPSC_U    = 0.0035   # deformación última del hormigón (EC8)
SL_FACTOR = 0.75     # 75% εcu → límite de servicio
NC_FACTOR = 1.25     # 125% εcu → colapso
```

**Nota de diseño:** `capture_limit_state_step` hace un solo recorrido de elementos por paso, alimentando simultáneamente `yield_history` (visualización de rótulas) y `floor_limit_states` (curva pushover). Reemplaza a los eliminados `SteelYieldDetector` y `CodeLimitStateDetector`.

## Cache de Análisis Pushover

```python
# Resultados
self.pushover_results = None      # Diccionario de resultados
self.yield_history = []            # Historia de fluencia por paso
self.pushover_loads = []          # Cargas temporales pushover

# Invalidados cuando:
# - mark_topology_dirty()
# - delete_pattern()
# - new_project()
```

## get_floor_data()

Agrupación de nodos y elementos por cota Y:
- Tolerancia de 1mm para agrupar
- Clasifica elementos como columnas o vigas
- Retorna diccionario ordenado por altura

## get_floor_masses()

Cálculo de masas por planta:
- Masas nodales concentradas
- Masa de vigas (L × ρ)
- Masa de columnas (½ para piso actual, ½ para inferior)

## Relaciones

```
ProjectManager (Singleton)
├── UI Layer ──► dataChanged signal
├── Dialogs ──► Almacenan/leen datos
├── OpenSeesTranslator ──► Lee datos para análisis
├── ModelBuilder ──► Lee datos para construir modelo
├── PushoverSolver ──► Llama reset/capture_limit_state_*
├── AnimationToolbar ──► Lee yield_history
├── PushoverResultsWidget ──► Lee floor_limit_states vía results["limit_states"]
├── LoadRenderer ──► Lee pushover_loads
└── ScaleManager ──► autocalculate_scales()
```

## Relacionado Con

- [[OpenSeesTranslator]] - Ejecuta análisis usando Manager
- [[ModelBuilder]] - Construye modelo desde Manager
- [[Node]] / [[Element]] / [[Materials]] / [[Sections]] / [[Loads]] - Datos almacenados
- [[AnimationToolbar]] - Consume resultados
- [[MainWindow]] - Recibe dataChanged