---
name: DefineMenu
description: Menú para definir materiales, secciones, geometría, patrones y grilla
type: reference
---

# DefineMenu

Menú `QMenu` que abre los diálogos de definición de entidades del modelo.

**Clase:** `DefineMenu(QMenu)`  
**Archivo:** `src/ui/menus/define_menu.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `setup_actions()` | Crea y conecta todas las acciones del menú |
| `open_material_dialog()` | Abre `MaterialDialog` |
| `open_section_dialog()` | Abre `SectionDialog` |
| `open_geometry_dialog()` | Abre `GeometryDialog` |
| `open_pattern_dialog()` | Abre `PatternDialog` |

## Acciones del menú

| Acción | Función |
|-------|---------|
| Materiales | `open_material_dialog()` |
| Secciones | `open_section_dialog()` |
| Geometría (Nodos/Elementos) | `open_geometry_dialog()` |
| Patrones de Carga | `open_pattern_dialog()` |
| Grilla | `gridDialog` (vía `ToolsMenu`) |

## Relaciones

```
DefineMenu
├── MaterialDialog ──► open_material_dialog()
├── SectionDialog ──► open_section_dialog()
├── GeometryDialog ──► open_geometry_dialog()
├── PatternDialog ──► open_pattern_dialog()
└── MainWindow ──► lo instancia
```

## Relacionado Con

- [[MaterialDialog]] - Gestión de materiales
- [[SectionDialog]] - Gestión de secciones
- [[GeometryDialog]] - Gestión de nodos y elementos
- [[PatternDialog]] - Gestión de patrones de carga
- [[Menus]] - Índice de menús
