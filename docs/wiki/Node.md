# Node

Clase que representa un nodo en el modelo estructural.

## Clase
`Node`

## Propósito
Representa un punto en el modelo estructural con coordenadas, restricciones y masas.

## Atributos

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `tag` | int | Identificador único del nodo |
| `x` | float | Coordenada X |
| `y` | float | Coordenada Y |
| `fixity` | list | Restricciones [fx, fy, mz] (1=fijo, 0=libre) |
| `mass` | list/None | Masas concentradas [mx, my, mrz] |

## Métodos

| Método | Descripción | Retorna |
|--------|-------------|---------|
| `to_dict()` | Serializa a diccionario para guardar en JSON | dict |
| `from_dict(data)` | Factory method para reconstruir desde JSON | Node |
| `get_opensees_command()` | Genera comando OpenSees | str |
| `__repr__()` | Representación de debug | str |

## Serialización

```python
# Guardar
data = node.to_dict()

# Cargar
node = Node.from_dict(data)
```

## Ejemplo

```python
# Nodo libre con masa
node = Node(tag=1, x=0.0, y=0.0, fixity=[1, 1, 1], mass=[1000, 1000, 0])

# Nodo libre sin masa
node = Node(tag=2, x=3.0, y=3.0)
```

## Relaciones

```
Node
├── Manager.add_node() ──► Lo almacena
├── Manager.get_node() ──► Lo recupera
├── Manager.get_all_nodes() ──► Lista todos
├── Manager.get_floor_data() ──► Agrupa por planta
├── Manager.get_floor_masses() ──► Calcula masas
├── ModelBuilder._build_nodes() ──► Crea en OpenSees
├── LoadPushoverGenerator._identify_master_nodes() ──► Nodos de control
├── PushoverSolver._get_base_shear() ──► Reacciones
└── GeometryDialog ──► UI para crear nodos
```

## Relacionado Con

- [[ProjectManager]] - Gestiona los nodos del proyecto
- [[Element]] - Elementos conectados a nodos
- [[ModelBuilder]] - Construye nodos en OpenSees
- [[GeometryDialog]] - UI para crear/modificar nodos