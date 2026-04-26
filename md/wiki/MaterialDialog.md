---
name: MaterialDialog
description: Diálogo modal para crear, editar y eliminar materiales uniaxiales
type: reference
---

# MaterialDialog

Diálogo modal para gestionar materiales uniaxiales del modelo.

**Clase:** `MaterialDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/material_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `__init__()` | Configura UI con `QStackedWidget` de formularios por tipo |
| `load_materials()` | Pobla `QListWidget` con materiales del manager |
| `on_material_selected()` | Rellena formulario al seleccionar ítem de la lista |
| `add_material()` | Crea material desde formulario activo y lo añade al manager |
| `update_material()` | Actualiza material seleccionado con datos del formulario |
| `delete_material()` | Elimina material seleccionado del manager |

## Tipos soportados

`Concrete01` · `Steel01` · `Elastic` · `Hysteretic` · `HystereticSM`

Cada tipo tiene su propio formulario (ver [[MaterialForms]]).

## Relaciones

```
MaterialDialog
├── ProjectManager ──► add/delete/update material
├── MaterialForms ──► formularios por tipo
└── DefineMenu ──► lo abre con exec()
```

## Relacionado Con

- [[Materials]] - Clases de material
- [[MaterialForms]] - Formularios de entrada
- [[DefineMenu]] - Menú que lo abre
- [[ProjectManager]] - Almacena materiales
