---
name: PatternDialog
description: Diálogo modal para gestionar patrones de carga
type: reference
---

# PatternDialog

Diálogo modal para crear, editar y eliminar `LoadPattern`.

**Clase:** `PatternDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/pattern_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `load_patterns()` | Pobla lista con patrones del manager |
| `on_pattern_selected()` | Rellena formulario (nombre, factor) al seleccionar |
| `add_pattern()` | Crea `LoadPattern` con nombre y factor del formulario |
| `update_pattern()` | Actualiza nombre y factor del patrón seleccionado |
| `delete_pattern()` | Elimina patrón seleccionado y sus cargas |

## Campos del formulario

- Nombre del patrón
- Factor multiplicador (`factor`)

## Relaciones

```
PatternDialog
├── ProjectManager ──► CRUD patrones
├── LoadPattern ──► crea instancias
└── DefineMenu ──► lo abre
```

## Relacionado Con

- [[Loads]] - Sistema de cargas
- [[LoadPattern]] - Clase patrón
- [[DefineMenu]] - Menú que lo abre
- [[NodalLoadsDialog]] - Asigna cargas al patrón
- [[ElementLoadsDialog]] - Asigna cargas al patrón
