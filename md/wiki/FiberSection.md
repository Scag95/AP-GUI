---
name: FiberSection
description: Sección transversal de fibra con patches rectangulares y layers de refuerzo
type: reference
---

# FiberSection

Sección de fibra de OpenSees construida con `RectPatch` y `LayerStraight`. Hereda de `Section`.

**Clase:** `FiberSection(Section)`  
**Archivo:** `src/analysis/sections.py`

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `tag` | `int` | ID de sección |
| `name` | `str` | Nombre descriptivo |
| `patches` | `list[RectPatch]` | Patches rectangulares de concreto |
| `layers` | `list[LayerStraight]` | Capas de refuerzo |

## Métodos

| Método | Descripción |
|-------|-------------|
| `add_rect_patch(patch)` | Añade un `RectPatch` |
| `add_layer_straight(layer)` | Añade un `LayerStraight` |
| `get_opensees_commands()` | Genera `ops.section('Fiber', ...)` con todos los patches y layers |
| `get_mass_per_length(material_manager)` | Calcula masa lineal desde densidad del material y área de patches |
| `to_dict()` / `from_dict(data)` | Serialización JSON |

## Relaciones

```
FiberSection
├── Section ──► clase base
├── RectPatch ──► patches[]
├── LayerStraight ──► layers[]
├── ForceBeamColumn ──► usa section_tag
├── SectionDialog ──► crea/edita
└── SectionPreview ──► visualiza
```

## Relacionado Con

- [[Sections]] - Jerarquía de secciones
- [[SectionDialog]] - Gestión desde UI
- [[SectionPreview]] - Visualización
- [[ForceBeamColumn]] - Elemento que la usa
