---
name: PropertiesForms
description: Formularios inline de edición de nodos y elementos para el PropertiesPanel
type: reference
---

# PropertiesForms

Formularios `QWidget` que se muestran en el `PropertiesPanel` al seleccionar un nodo o elemento en el viewport. Permiten editar y guardar propiedades directamente.

**Archivo:** `src/ui/widgets/properties_forms.py`

## Clases

### NodeForms(QWidget)

Formulario de edición de nodo.

| Función | Descripción |
|--------|-------------|
| `load_node(node)` | Carga coordenadas y fixity del nodo en los campos |
| `apply_changes()` | Actualiza el nodo en el manager y emite `dataChanged` |
| `_on_value_changed()` | Marca el formulario como modificado |

**Señales:** `dataChanged`

### ElementForm(QWidget)

Formulario de edición de elemento.

| Función | Descripción |
|--------|-------------|
| `load_element(element)` | Carga nodos, sección y propiedades del elemento |
| `apply_changes()` | Actualiza el elemento en el manager y emite `dataChanged` |
| `_on_value_changed()` | Marca el formulario como modificado |

**Señales:** `dataChanged`

## Relaciones

```
PropertiesForms
├── PropertiesPanel ──► embebe NodeForms y ElementForm en QStackedWidget
├── ProjectManager ──► get/update nodo y elemento
└── StructureInteractor ──► dispara selección
```

## Relacionado Con

- [[PropertiesPanel]] - Panel dock que los contiene
- [[Node]] - Nodo editado
- [[Element]] - Elemento editado
- [[Widgets]] - Índice de widgets
