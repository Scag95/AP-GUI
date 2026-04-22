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
├── material{}        # tag → Material
├── section{}        # tag → Section
├── node{}          # tag → Node
├── element{}        # tag → Element
├── patterns{}       # tag → LoadPattern
├── gravity_results # dict o None
├── pushover_results # dict o None
├── yield_history   # list
├── pushover_loads   # list
└── _floors_cache  # dict (privado)
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
├── AnimationToolbar ──► Lee pushover_results
├── LoadRenderer ──► Lee pushover_loads
└── ScaleManager ──► autocalculate_scales()
```

## Relacionado Con

- [[OpenSeesTranslator]] - Ejecuta análisis usando Manager
- [[ModelBuilder]] - Construye modelo desde Manager
- [[Node]] / [[Element]] / [[Materials]] / [[Sections]] / [[Loads]] - Datos almacenados
- [[AnimationToolbar]] - Consume resultados
- [[MainWindow]] - Recibe dataChanged