---
name: PropertiesPanel
description: Panel dock que muestra el formulario de propiedades del nodo o elemento seleccionado
type: reference
---

# PropertiesPanel

`QDockWidget` lateral que usa un `QStackedWidget` para mostrar `NodeForms` o `ElementForm` según la selección en el viewport. Emite `dataChanged` cuando el usuario edita propiedades.

**Clase:** `PropertiesPanel(QDockWidget)`  
**Archivo:** `src/ui/widgets/properties_panel.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `show_node(node)` | Carga el nodo en `NodeForms` y lo muestra en el stack |
| `show_element(element)` | Carga el elemento en `ElementForm` y lo muestra en el stack |
| `clear_selection()` | Vuelve al mensaje placeholder "Seleccione un elemento" |

## Señales

| Señal | Descripción |
|------|-------------|
| `dataChanged` | Re-emitida desde `NodeForms.dataChanged` y `ElementForm.dataChanged` |

## Relaciones

```
PropertiesPanel
├── NodeForms ──► formulario inline de nodo
├── ElementForm ──► formulario inline de elemento
├── StructureInteractor ──► dispara show_node/show_element al seleccionar
└── MainWindow ──► lo aloja como dock derecho
```

## Relacionado Con

- [[PropertiesForms]] - NodeForms y ElementForm que contiene
- [[StructureInteractor]] - Dispara la selección
- [[MainWindow]] - Aloja el dock
- [[Widgets]] - Índice de widgets
