---
name: SectionDialog
description: Diálogo modal para crear, editar y previsualizar secciones de fibra
type: reference
---

# SectionDialog

Diálogo modal para gestionar secciones transversales (`FiberSection` y `AggregatorSection`).

**Clase:** `SectionDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/section_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `__init__()` | Configura UI con tabs (FiberSection / Aggregator) y panel de preview |
| `load_sections()` | Pobla lista con secciones del manager |
| `on_section_selected()` | Rellena formulario y actualiza preview al seleccionar |
| `add_section()` | Crea sección desde formulario activo |
| `update_section()` | Actualiza sección seleccionada |
| `delete_section()` | Elimina sección seleccionada |
| `update_preview()` | Llama `SectionPreview.plot_section()` con sección temporal |
| `_build_section_from_form()` | Construye `FiberSection` temporal para preview |
| `_setup_section_geometry()` | Configura patches y layers desde datos del formulario |
| `on_tab_changed()` | Repobla combos de materiales al cambiar de tab |

## Relaciones

```
SectionDialog
├── ProjectManager ──► add/delete/update section
├── SectionForms ──► SectionForm y AggregatorForm
├── SectionPreview ──► previsualiza sección
└── DefineMenu ──► lo abre
```

## Relacionado Con

- [[Sections]] - Clases de sección
- [[SectionForms]] - Formularios de entrada
- [[SectionPreview]] - Vista previa visual
- [[DefineMenu]] - Menú que lo abre
