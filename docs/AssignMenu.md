---
name: AssignMenu
description: Menú para asignar cargas nodales, cargas de elemento y restricciones
type: reference
---

# AssignMenu

Menú `QMenu` que agrupa las acciones de asignación de cargas y restricciones a nodos y elementos.

**Clase:** `AssignMenu(QMenu)`  
**Archivo:** `src/ui/menus/assign_menu.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `open_element_loads()` | Abre `ElementLoadsDialog` |
| `open_nodal_loads()` | Abre `NodalLoadsDialog` |
| `open_restraints()` | Abre `RestraintsDialog` |

## Acciones del menú

| Acción | Función |
|-------|---------|
| Cargas de Elemento | `open_element_loads()` |
| Cargas Nodales | `open_nodal_loads()` |
| Restricciones | `open_restraints()` |

## Relaciones

```
AssignMenu
├── ElementLoadsDialog ──► open_element_loads()
├── NodalLoadsDialog ──► open_nodal_loads()
├── RestraintsDialog ──► open_restraints()
└── MainWindow ──► lo instancia
```

## Relacionado Con

- [[ElementLoadsDialog]] - Cargas distribuidas en elementos
- [[NodalLoadsDialog]] - Cargas puntuales en nodos
- [[RestraintsDialog]] - Restricciones DOF
- [[Menus]] - Índice de menús
