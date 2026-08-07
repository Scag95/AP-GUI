---
name: SectionForms
description: Formularios de entrada para FiberSection y AggregatorSection
type: reference
---

# SectionForms

Widgets de formulario usados por `SectionDialog` para definir secciones transversales.

**Archivo:** `src/ui/widgets/section_forms.py`

## Clases

### SectionForm(QWidget)

Formulario para `FiberSection`: patches rectangulares y layers de refuerzo.

| Función | Descripción |
|--------|-------------|
| `get_data()` | Retorna dict con patches (concreto recubierto/núcleo) y layers (refuerzo) |
| `set_data(section)` | Carga los parámetros de una `FiberSection` en los campos |

**Campos:** nombre, material núcleo/recubrimiento, b/h total, e_cover, n_bars, diam_bar, n_fibers.

### AggregatorForm(QWidget)

Formulario para `AggregatorSection`: agrega materiales por DOF.

| Función | Descripción |
|--------|-------------|
| `get_data()` | Retorna dict con la sección base y los materiales agregados por DOF |
| `set_data(section)` | Carga parámetros de una `AggregatorSection` |

## Relaciones

```
SectionForms
├── SectionDialog ──► los embebe en tabs
├── Sections ──► FiberSection, AggregatorSection
└── Materials ──► seleccionados vía combo
```

## Relacionado Con

- [[SectionDialog]] - Contenedor que usa estos forms
- [[Sections]] - Secciones resultantes
- [[SectionPreview]] - Preview visual del form activo
- [[Widgets]] - Índice de widgets
