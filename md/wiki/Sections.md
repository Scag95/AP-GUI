# Sections

Clases para secciones transversales de elementos estructurales.

## Clases Auxiliares

### RectPatch

Parche rectangular para FiberSection.

```python
class RectPatch:
    __slots__ = ['material_tag', 'yI', 'zI', 'yJ', 'zJ', 'nIy', 'nIz']
```

| Atributo | Descripción |
|----------|-------------|
| `material_tag` | Tag del material (concreto) |
| `yI, zI` | Coordenadas esquina inferior |
| `yJ, zJ` | Coordenadas esquina superior |
| `nIy, nIz` | Subdivisiones para integración |

### LayerStraight

Capa de barras de acero.

```python
class LayerStraight:
    __slots__ = ['material_tag', 'num_bars', 'area_bar', 'yStart', 'zStart', 'yEnd', 'zEnd']
```

| Atributo | Descripción |
|----------|-------------|
| `material_tag` | Tag del material (acero) |
| `num_bars` | Número de barras |
| `area_bar` | Área de cada barra |
| `yStart, zStart` | Coordenadas inicio |
| `yEnd, zEnd` | Coordenadas fin |

## Clases Principales

### Section (Base)

```python
class Section:
    __slots__ = ['tag', 'name']
```

### FiberSection → [[FiberSection]]

Sección de fibra con parches de concreto y capas de acero.

```python
class FiberSection(Section):
    __slots__ = ['patches', 'layers']
```

### AggregatorSection → [[AggregatorSection]]

Sección agregada que combina FiberSection con materiales para otros DOFs.

```python
class AggregatorSection(Section):
    __slots__ = ['base_section_tag', 'materials']
```

## Métodos por Clase

| Clase | Método | Descripción | Retorna |
|-------|-------|-------------|---------|
| RectPatch | `to_dict()` / `from_dict()` | Serialización | dict |
| LayerStraight | `to_dict()` / `from_dict()` | Serialización | dict |
| Section | `to_dict()` | Serialización base | dict |
| FiberSection | `add_rect_patch()` | Añade parche | None |
| FiberSection | `add_layer_straight()` | Añade capa | None |
| FiberSection | `get_opensees_commands()` | Comandos OpenSees | list |
| FiberSection | `get_mass_per_length()` | Masa por unidad | float |
| FiberSection | `to_dict()` / `from_dict()` | Serialización | dict |
| AggregatorSection | `add_material()` | Añade material a DOF | None |
| AggregatorSection | `get_opensees_commands()` | Comandos OpenSees | list |
| AggregatorSection | `get_mass_per_length()` | Delega a base | float |
| AggregatorSection | `to_dict()` / `from_dict()` | Serialización | dict |

## Geometría Estándar

```
    ┌─────────────────────┐
    │ ═══════════════════ │ ← Acero Superior (LayerStraight)
    │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ ← Parche Concreto (RectPatch)
    │ ═══════════════════ │ ← Acero Inferior (LayerStraight)
    └─────────────────────┘
        ↑                ↑
     cover           cover
```

## Relaciones con OpenSees

```
FiberSection
    ├── section Fiber {tag}
    │   ├── patch rect {mat} {nIy} {nIz} {yI} {zI} {yJ} {zJ}
    │   └── layer straight {mat} {num} {area} {yS} {zS} {yE} {zE}
    └── section Aggregator {tag} {shearMat} Vy -section {fiberTag}
```

## Relaciones

```
Section
├── Manager.add_section() ──► Lo almacena
├── Manager.get_section() ──► Lo recupera
├── Manager.get_all_sections() ──► Lista todas
├── ModelBuilder._build_sections() ──► Crea en OpenSees
├── Element.mass_density ──► Calculado desde sección
├── ProjectManager._ls_*() ──► Detecta fluencia y estados límite por sección
└── SectionDialog ──► UI para crear secciones
```

## Relacionado Con

- [[ProjectManager]] - Gestiona secciones
- [[ModelBuilder]] - Construye secciones en OpenSees
- [[Materials]] - Materiales usados en patches y layers
- [[Element]] - Elementos que usan secciones
- [[SectionDialog]] - UI para crear/modificar secciones