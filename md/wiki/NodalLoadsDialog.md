---
name: NodalLoadsDialog
description: Diálogo modal para asignar cargas puntuales a nodos
type: reference
---

# NodalLoadsDialog

Diálogo modal para asignar `NodalLoad` a nodos con selección por texto o lista.

**Clase:** `NodalLoadsDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/nodal_loads_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `populate_patterns()` | Pobla combo con patrones disponibles |
| `populate_nodes()` | Pobla lista de nodos (con cargas existentes indicadas) |
| `select_from_text()` | Selecciona en la lista los IDs escritos en el campo de texto |
| `_parse_input(text)` | Convierte "1,3-5" en lista de IDs |
| `apply_loads()` | Crea/reemplaza `NodalLoad` en nodos seleccionados |
| `clear_loads()` | Elimina cargas de los nodos seleccionados |
| `on_node_selected()` | Rellena campos Fx/Fy/Mz al seleccionar un nodo |

## Controles

- Campo de texto para IDs (soporta rangos: `1,3-5,8`)
- `QListWidget` con selección múltiple
- Selector de patrón destino
- `UnitSpinBox` para Fx, Fy, Mz

## Relaciones

```
NodalLoadsDialog
├── ProjectManager ──► add/delete load
├── NodalLoad ──► crea instancias
├── LoadPattern ──► patrón destino
└── AssignMenu ──► lo abre
```

## Relacionado Con

- [[Loads]] - Sistema de cargas
- [[NodalLoad]] - Clase de carga nodal
- [[LoadPattern]] - Patrón contenedor
- [[AssignMenu]] - Menú que lo abre
