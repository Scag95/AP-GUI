---
name: ToolsMenu
description: Menú de herramientas auxiliares (grilla, peso propio, unidades)
type: reference
---

# ToolsMenu

Menú `QMenu` con herramientas de generación automática y configuración del sistema de unidades.

**Clase:** `ToolsMenu(QMenu)`  
**Archivo:** `src/ui/menus/tools_menu.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `open_self_weight_dialog()` | Abre `SelfWeightDialog` para generar cargas de peso propio |
| `show_grid_dialog()` | Abre `gridDialog` y si el usuario acepta, llama a `FrameGenerator` con los datos |

## Acciones del menú

| Acción | Función |
|-------|---------|
| Peso Propio | `open_self_weight_dialog()` |
| Generar Grilla | `show_grid_dialog()` |

## Relaciones

```
ToolsMenu
├── SelfWeightDialog ──► open_self_weight_dialog()
├── GridDialog ──► show_grid_dialog()
├── FrameGenerator ──► genera malla con datos del GridDialog
└── MainWindow ──► lo instancia
```

## Relacionado Con

- [[SelfWeightDialog]] - Generación de peso propio
- [[GridDialog]] - Configuración de grilla
- [[FrameGenerator]] - Generador de mallas de pórtico
- [[Menus]] - Índice de menús
