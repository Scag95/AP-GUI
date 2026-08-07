---
name: AggregatorSection
description: Sección agregadora que combina materiales uniaxiales por grado de libertad
type: reference
---

# AggregatorSection

Sección `SectionAggregator` de OpenSees: combina una sección base con materiales adicionales para DOF específicos (P, Vy, Mz, etc.). Hereda de `Section`.

**Clase:** `AggregatorSection(Section)`  
**Archivo:** `src/analysis/sections.py`

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `tag` | `int` | ID de sección |
| `name` | `str` | Nombre descriptivo |
| `base_section_tag` | `int\|None` | Sección base (FiberSection) opcional |
| `materials` | `list[tuple]` | Lista de `(mat_tag, dof_str)` |

## Métodos

| Método | Descripción |
|-------|-------------|
| `add_material(mat_tag, dof)` | Añade un par `(mat_tag, dof)` a la lista |
| `get_opensees_commands()` | Genera `ops.section('Aggregator', ...)` |
| `get_mass_per_length(material_manager)` | Delega en la sección base si existe |
| `to_dict()` / `from_dict(data)` | Serialización JSON |

## Relaciones

```
AggregatorSection
├── Section ──► clase base
├── FiberSection ──► base_section_tag (opcional)
├── Materials ──► materiales asignados por DOF
└── SectionDialog ──► tab AggregatorForm
```

## Relacionado Con

- [[Sections]] - Jerarquía de secciones
- [[FiberSection]] - Sección base opcional
- [[SectionDialog]] - Gestión desde UI
- [[SectionForms]] - `AggregatorForm`
