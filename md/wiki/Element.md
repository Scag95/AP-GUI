# Element

Clases base y especializadas para elementos estructurales.

## Clase Base: Element

```python
class Element:
    __slots__ = ['tag', 'node_i', 'node_j']
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `tag` | int | Identificador único |
| `node_i` | int | Tag del nodo inicial |
| `node_j` | int | Tag del nodo final |

### Métodos

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `to_dict()` | Serializa a diccionario | dict |
| `from_dict(data)` | Reconstruye desde diccionario | Element |

---

## ForceBeamColumn

Elemento viga-columna con integración de Gauss-Lobatto.

```python
class ForceBeamColumn(Element):
    __slots__ = ['integration_points', 'section_tag', 'transf_tag', 'mass_density']
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `integration_points` | int | Número de puntos de integración (3, 5, 7, etc.) |
| `section_tag` | int | Tag de la sección de fibra |
| `transf_tag` | int | Tag de transformación geométrica |
| `mass_density` | float | Densidad de masa para análisis dinámico |

### Métodos

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `get_opensees_command()` | Genera comando OpenSees | str |
| `to_dict()` | Serializa a diccionario | dict |
| `from_dict(data)` | Reconstruye desde diccionario | ForceBeamColumn |

---

## ForceBeamColumnHinge

Elemento viga-columna con bisagras plásticas en los extremos (integración HingeRadau).

```python
class ForceBeamColumnHinge(Element):
    __slots__ = ['transf_tag', 'section_i_tag', 'lp_i', 'section_j_tag', 'lp_j', 'section_e_tag', 'mass_density']
```

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `transf_tag` | int | Tag de transformación geométrica |
| `section_i_tag` | int | Sección en extremo i |
| `lp_i` | float | Longitud de penetración de bisagra en i |
| `section_j_tag` | int | Sección en extremo j |
| `lp_j` | float | Longitud de penetración de bisagra en j |
| `section_e_tag` | int | Sección elástica (interior) |
| `mass_density` | float | Densidad de masa |

### Property

| Property | Descripción | Retorna |
|----------|-------------|---------|
| `integration_points` | Retorna 6 (fijo para HingeRadau) | int |

### Métodos

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `to_dict()` | Serializa a diccionario | dict |
| `from_dict(data)` | Reconstruye desde diccionario | ForceBeamColumnHinge |

## Relaciones

```
Element
├── Manager.add_element() ──► Lo almacena
├── Manager.get_element() ──► Lo recupera
├── Manager.get_all_elements() ──► Lista todos
├── Manager.get_floor_data() ──► Clasifica por planta
├── ModelBuilder._build_elements() ──► Crea en OpenSees
├── SteelYieldDetector.capture_step() ──► Lee resultados
└── FailureDetector ──► Analiza fuerzas
```

## Relacionado Con

- [[Node]] - Nodos conectados
- [[Sections]] - Secciones de fibra
- [[ModelBuilder]] - Construye elementos en OpenSees
- [[ProjectManager]] - Gestiona elementos
- [[Solvers]] - Usan elementos para análisis