---
name: FileMenu
description: Menú de gestión de proyectos (nuevo, guardar, cargar, salir)
type: reference
---

# FileMenu

Menú `QMenu` que gestiona el ciclo de vida del proyecto: nuevo, guardar JSON, cargar JSON y salir.

**Clase:** `FileMenu(QMenu)`  
**Archivo:** `src/ui/menus/file_menu.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `setup_actions()` | Crea y conecta las acciones del menú |
| `open_save_dialog()` | Abre `QFileDialog` y serializa el proyecto a JSON vía `ProjectManager` |
| `open_load_dialog()` | Abre `QFileDialog` y deserializa un JSON de proyecto |
| `open_new_project()` | Resetea el manager y limpia el viewport |

## Acciones del menú

| Acción | Atajo | Función |
|-------|-------|---------|
| Nuevo Proyecto | - | `open_new_project()` |
| Guardar Proyecto | Ctrl+S | `open_save_dialog()` |
| Cargar Proyecto | Ctrl+O | `open_load_dialog()` |
| Salir | - | `QApplication.quit()` |

## Relaciones

```
FileMenu
├── ProjectManager ──► save_project(), load_project(), new_project()
└── MainWindow ──► lo instancia
```

## Relacionado Con

- [[ProjectManager]] - Serialización/deserialización del proyecto
- [[MainWindow]] - Contiene el menú
- [[Menus]] - Índice de menús
