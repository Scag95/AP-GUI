---
name: ForceBeamColumn
description: Elemento viga-columna de plasticidad distribuida con integración de Gauss-Lobatto
type: reference
---

# ForceBeamColumn

Elemento `forceBeamColumn` de OpenSees con integración distribuida. Hereda de `Element`.

**Clase:** `ForceBeamColumn(Element)`  
**Archivo:** `src/analysis/element.py`

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `tag` | `int` | ID del elemento |
| `node_i`, `node_j` | `int` | Nodos extremos |
| `section_tag` | `int` | Sección de fibra asignada |
| `transf_tag` | `int` | Transformación geométrica |
| `integration_points` | `int` | Número de puntos de integración (3–10) |
| `mass_density` | `float` | Densidad de masa lineal [kg/m] |

## Métodos

| Método | Descripción |
|-------|-------------|
| `get_opensees_command()` | Retorna la cadena `ops.element('forceBeamColumn', ...)` |
| `to_dict()` | Serializa para JSON |
| `from_dict(data)` | Reconstruye desde dict |

## Relaciones

```
ForceBeamColumn
├── Element ──► clase base
├── FiberSection ──► section_tag
├── ProjectManager ──► get_all_elements()
└── GeometryDialog ──► crea instancias
```

## Relacionado Con

- [[Element]] - Clase base y jerarquía de elementos
- [[FiberSection]] - Sección asignada
- [[GeometryDialog]] - Creación desde UI
