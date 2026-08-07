---
name: GeometryDialog
description: Diálogo modal para crear y modificar nodos y elementos individualmente
type: reference
---

# GeometryDialog

Diálogo modal con dos pestañas: **Nodos** y **Elementos**.

**Clase:** `GeometryDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/geometry_dialog.py`

## Funciones — Nodos

| Función | Descripción |
|--------|-------------|
| `setup_nodes_tab()` | Configura pestaña con formulario + lista de nodos |
| `on_add_node_clicked()` | Crea nodo con coordenadas del formulario |
| `refresh_node_list()` | Actualiza lista de nodos |
| `on_node_selected()` | Rellena formulario con datos del nodo seleccionado |
| `delete_node()` | Elimina nodo seleccionado |
| `update_node()` | Actualiza coordenadas y restricciones del nodo |

## Funciones — Elementos

| Función | Descripción |
|--------|-------------|
| `setup_elements_tab()` | Configura pestaña con combos y lista de elementos |
| `load_data()` | Pobla combos de nodos y secciones |
| `on_add_element_clicked()` | Crea elemento con parámetros del formulario |
| `on_element_selected()` | Rellena formulario al seleccionar elemento |
| `delete_element()` | Elimina elemento seleccionado |
| `update_element()` | Actualiza topología y sección |
| `on_element_type_changed()` | Muestra/oculta campos de bisagra plástica (`ForceBeamColumnHinge`) |

## Relaciones

```
GeometryDialog
├── ProjectManager ──► CRUD nodos y elementos
├── Node / Element ──► crea instancias
└── DefineMenu ──► lo abre
```

## Relacionado Con

- [[Node]] - Nodos creados
- [[Element]] - Elementos creados
- [[DefineMenu]] - Menú que lo abre
- [[ProjectManager]] - Almacena datos
