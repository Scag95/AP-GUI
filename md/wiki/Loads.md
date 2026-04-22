# Loads

Sistema de cargas y patrones de carga para análisis estructural.

## Clase Base: Load

```python
class Load(ABC):
    __slots__ = ['tag']
```

Clase abstracta base para cargas.

## Clases

### NodalLoad

Carga puntual aplicada en un nodo.

```python
class NodalLoad(Load):
    __slots__ = ['node_tag', 'fx', 'fy', 'mz']
```

| Atributo | Descripción |
|----------|-------------|
| `node_tag` | Tag del nodo destino |
| `fx` | Fuerza en X |
| `fy` | Fuerza en Y |
| `mz` | Momento alrededor de Z |

### ElementLoad

Carga distribuida uniforme en elemento.

```python
class ElementLoad(Load):
    __slots__ = ['element_tag', 'wx', 'wy']
```

| Atributo | Descripción |
|----------|-------------|
| `element_tag` | Tag del elemento |
| `wx` | Carga distribuida en X (axial) |
| `wy` | Carga distribuida en Y (transversal) |

### LoadPattern

Patrón de carga que agrupa múltiples cargas.

```python
class LoadPattern:
    __slots__ = ['tag', 'name', 'factor', 'loads']
```

| Atributo | Descripción |
|----------|-------------|
| `tag` | Identificador único |
| `name` | Nombre descriptivo |
| `factor` | Factor multiplicador (-fact) |
| `loads` | Lista de cargas (NodalLoad o ElementLoad) |

## Métodos por Clase

| Clase | Método | Descripción | Retorna |
|-------|-------|-------------|---------|
| Load | `to_dict()` | Serializa a diccionario | dict |
| Load | `from_dict()` | Factory method | Load |
| NodalLoad | `to_dict()` / `from_dict()` | Serialización | dict |
| ElementLoad | `to_dict()` / `from_dict()` | Serialización | dict |
| LoadPattern | `add_load(load_obj)` | Añade carga al patrón | None |
| LoadPattern | `remove_load(load_tag)` | Elimina carga por tag | None |
| LoadPattern | `to_dict()` / `from_dict()` | Serialización con loads hijos | dict |

## Serialización

```python
# Guardar patrón completo
data = pattern.to_dict()

# Cargar patrón completo
pattern = LoadPattern.from_dict(data)
```

## Relaciones con OpenSees

```
LoadPattern (tag)
    ├── timeSeries 'Linear' (tag)
    ├── pattern 'Plain' (tag, ts_tag, -fact, factor)
    │   ├── load(node, fx, fy, mz)    ← NodalLoad
    │   └── eleLoad(-ele, ..., -type, -beamUniform, wy, wx) ← ElementLoad
```

## Relaciones

```
LoadPattern
├── Manager.add_pattern() ──► Lo almacena
├── Manager.get_pattern() ──► Lo recupera
├── Manager.get_all_patterns() ──► Lista todos
├── ModelBuilder._build_patterns() ──► Crea en OpenSees
├── LoadPushoverGenerator ──► Genera vectores de carga
├── PushoverSolver ──► Usa patrones para pushover
└── PatternDialog ──► UI para gestionar patrones
```

## Relacionado Con

- [[ProjectManager]] - Gestiona patrones
- [[ModelBuilder]] - Construye patrones en OpenSees
- [[PatternDialog]] - UI para gestionar patrones
- [[NodalLoadsDialog]] - UI para asignar cargas nodales
- [[ElementLoadsDialog]] - UI para asignar cargas en elementos
- [[LoadPushoverGenerator]] - Generador de vectores de carga
- [[PushoverSolver]] - Análisis pushover