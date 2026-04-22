# Materials

Modelos de materiales uniaxiales para OpenSees.

## Clases

### Material (Base)

```python
class Material:
    __slots__ = ['tag', 'name', 'rho']
```

| Atributo | Descripción |
|----------|-------------|
| `tag` | Identificador único |
| `name` | Nombre descriptivo |
| `rho` | Densidad de masa |

### Concrete01

Modelo de concreto de Takeda con degradación de resistencia.

```python
class Concrete01(Material):
    __slots__ = ['fpc', 'epsc0', 'fpcu', 'epsu', 'minmax']
```

| Atributo | Descripción |
|----------|-------------|
| `fpc` | Resistencia a compresión (negativo) |
| `epsc0` | Deformación en fc |
| `fpcu` | Resistencia residual |
| `epsu` | Deformación última |
| `minmax` | Límites opcionales de strain |

### Steel01

Modelo de acero bilinear con endurecimiento isotrópico.

```python
class Steel01(Material):
    __slots__ = ['Fy', 'E0', 'b', 'a1', 'a2', 'a3', 'a4', 'minmax']
```

| Atributo | Descripción |
|----------|-------------|
| `Fy` | Esfuerzo de fluencia |
| `E0` | Módulo de elasticidad |
| `b` | Ratio de endurecimiento (Eps/E0) |
| `a1-a4` | Parámetros de endurecimiento isotrópico |
| `minmax` | Límites opcionales de strain |

### Elastic

Material elástico lineal.

```python
class Elastic(Material):
    __slots__ = ['E']
```

| Atributo | Descripción |
|----------|-------------|
| `E` | Módulo de elasticidad |

### Hysteretic

Material histerético trilineal con pino y daño.

```python
class Hysteretic(Material):
    __slots__ = [
        's1p', 'e1p', 's2p', 'e2p', 's3p', 'e3p',  # Envolvente +
        's1n', 'e1n', 's2n', 'e2n', 's3n', 'e3n',  # Envolvente -
        'pinch_x', 'pinch_y', 'damage1', 'damage2', 'beta'
    ]
```

### HystereticSM

Variante de Hysteretic con 4 puntos por envolvente.

```python
class HystereticSM(Material):
    __slots__ = [
        's1p', 'e1p', 's2p', 'e2p', 's3p', 'e3p', 's4p', 'e4p',  # +
        's1n', 'e1n', 's2n', 'e2n', 's3n', 'e3n', 's4n', 'e4n',  # -
        'pinch_x', 'pinch_y', 'damage1', 'damage2', 'beta'
    ]
```

## Métodos por Clase

| Clase | Método | Descripción | Retorna |
|-------|-------|-------------|---------|
| Material | `to_dict()` | Serializa a diccionario | dict |
| Material | `from_dict()` | Factory method | Material |
| Material | `get_yield_strain()` | Deformación de fluencia | None |
| Concrete01 | `get_opensees_args()` | Args para OpenSees | list |
| Steel01 | `get_yield_strain()` | Fy / E0 | float |
| Steel01 | `get_opensees_args()` | Args para OpenSees | list |
| Elastic | `get_opensees_args()` | Args para OpenSees | list |
| Elastic | `create_internal()` | Crea material interno | Elastic |
| Hysteretic | `get_yield_strain()` | min(e1p, e1n) | float |
| Hysteretic | `get_opensees_args()` | Args para OpenSees | list |
| HystereticSM | `get_yield_strain()` | min(e1p, e1n) | float |
| HystereticSM | `get_opensees_args()` | Args para OpenSees | list |

## Serialización

```python
# Todas las clases
data = material.to_dict()
material = Concrete01.from_dict(data)
```

## Relaciones con OpenSees

```
Steel01
    └── uniaxialMaterial Steel01 {tag} {Fy} {E0} {b} {a1} {a2} {a3} {a4}
```

## Relaciones

```
Material
├── Manager.add_material() ──► Lo almacena
├── Manager.get_material() ──► Lo recupera
├── Manager.get_all_materials() ──► Lista todos
├── ModelBuilder._build_materials() ──► Crea en OpenSees
├── FiberSection ──► Usa en patches
├── LayerStraight ──► Usa en capas
├── SteelYieldDetector ──► Lee yield_strain
└── MaterialDialog ──► UI para crear materiales
```

## Relacionado Con

- [[ProjectManager]] - Gestiona materiales
- [[ModelBuilder]] - Construye materiales en OpenSees
- [[Sections]] - Secciones que usan materiales
- [[MaterialDialog]] - UI para crear materiales