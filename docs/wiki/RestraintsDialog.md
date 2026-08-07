---
name: RestraintsDialog
description: Diálogo modal para asignar y quitar restricciones de grados de libertad a nodos
type: reference
---

# RestraintsDialog

Diálogo modal para asignar restricciones DOF (UX, UY, RZ) a nodos, con selección por texto/rangos y botones de selección rápida.

**Clase:** `RestraintsDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/restraints_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `_setup_ui()` | Construye el layout: campo de texto, checkboxes DOF, lista y botones |
| `_quick_select(mode)` | Rellena el campo de texto con todos los nodos (`'all'`) o solo los del borde inferior (`'bottom'`) |
| `_parse_node_input()` | Convierte texto tipo `"1,3-5,8"` en lista de IDs enteros |
| `_on_apply()` | Aplica el fixity `[UX,UY,RZ]` a los nodos del campo de texto; emite `dataChanged` |
| `_on_remove()` | Pone `[0,0,0]` a los nodos seleccionados en la lista |
| `_refresh_list()` | Repobla la lista mostrando solo nodos con alguna restricción activa |

## Controles

- Campo de texto para IDs (rangos soportados: `1,3-5,8`)
- Botones rápidos: **Todos** / **Borde inferior** (detecta Y mínima con tolerancia 1e-4)
- Checkboxes `UX`, `UY`, `RZ`
- `QListWidget` mostrando nodos con restricción (`Nodo X: [1,1,0]`)
- Botones **Aplicar / Actualizar** y **Quitar Restricción**

## Relaciones

```
RestraintsDialog
├── ProjectManager ──► get_all_nodes(), get_node(), dataChanged.emit()
├── Node ──► fixity[3]
└── AssignMenu ──► lo abre
```

## Relacionado Con

- [[Node]] - Nodo con atributo `fixity`
- [[ProjectManager]] - Acceso a nodos y señal `dataChanged`
- [[AssignMenu]] - Menú que lo abre
