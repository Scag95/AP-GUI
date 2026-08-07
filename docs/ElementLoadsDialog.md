---
name: ElementLoadsDialog
description: Diálogo modal para asignar cargas distribuidas uniformes a elementos
type: reference
---

# ElementLoadsDialog

Diálogo modal para asignar `ElementLoad` (wx, wy) a elementos con selección por texto o lista.

**Clase:** `ElementLoadsDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/element_loads_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `populate_patterns()` | Pobla combo con patrones disponibles |
| `populate_elements()` | Lista elementos; filtra solo con carga si `chk_assigned_only` activo |
| `select_from_text()` | Selecciona en la lista los IDs escritos en el campo de texto |
| `_parse_input(text)` | Convierte "1,3-5" en lista de IDs |
| `apply_loads()` | Crea/reemplaza `ElementLoad` en elementos seleccionados |
| `clear_loads()` | Elimina cargas de elementos seleccionados |
| `_remove_load_for_element(element_tag)` | Borra la carga de un elemento del patrón activo |
| `on_element_selected()` | Rellena spinboxes wx/wy al seleccionar |
| `toggle_tags(checked)` | Muestra/oculta etiquetas de elementos en el viewport |

## Controles

- Campo de texto para IDs (rangos soportados)
- `chk_assigned_only` — filtra solo elementos con carga
- `chk_show_tags` — toggle etiquetas en viewport
- Selector de patrón destino
- `UnitSpinBox` wx y wy (tipo `DISTRIBUTED_FORCE`)

## Relaciones

```
ElementLoadsDialog
├── ProjectManager ──► add/delete load
├── ElementLoad ──► crea instancias
├── LoadPattern ──► patrón destino
└── AssignMenu ──► lo abre
```

## Relacionado Con

- [[Loads]] - Sistema de cargas
- [[ElementLoad]] - Clase de carga distribuida
- [[LoadPattern]] - Patrón contenedor
- [[AssignMenu]] - Menú que lo abre
