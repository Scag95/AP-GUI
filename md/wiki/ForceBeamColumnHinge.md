---
name: ForceBeamColumnHinge
description: Elemento viga-columna con plasticidad concentrada en rótulas usando integración HingeRadau
type: reference
---

# ForceBeamColumnHinge

Elemento con plasticidad concentrada en los extremos i y j mediante integración `HingeRadau` de OpenSees. Hereda de `Element`.

**Clase:** `ForceBeamColumnHinge(Element)`  
**Archivo:** `src/analysis/element.py`

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `tag` | `int` | ID del elemento |
| `node_i`, `node_j` | `int` | Nodos extremos |
| `section_i_tag` | `int` | Sección en rótula i |
| `lp_i` | `float` | Longitud de rótula i [m] |
| `section_j_tag` | `int` | Sección en rótula j |
| `lp_j` | `float` | Longitud de rótula j [m] |
| `section_e_tag` | `int` | Sección elástica interior |
| `transf_tag` | `int` | Transformación geométrica |
| `mass_density` | `float` | Densidad de masa lineal |

## Métodos

| Método | Descripción |
|-------|-------------|
| `integration_points` | Propiedad que retorna `5` (fijo para HingeRadau) |
| `to_dict()` | Serializa para JSON |
| `from_dict(data)` | Reconstruye desde dict |

## Relaciones

```
ForceBeamColumnHinge
├── Element ──► clase base
├── FiberSection ──► section_i, section_j, section_e
├── ProjectManager ──► almacena el elemento
└── GeometryDialog ──► on_element_type_changed() muestra campos Lp
```

## Relacionado Con

- [[Element]] - Jerarquía de elementos
- [[FiberSection]] - Secciones de rótula y elástica
- [[GeometryDialog]] - UI que expone los campos de rótula plástica
