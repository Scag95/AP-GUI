# MainWindow

Ventana principal de la aplicación.

## Clase
`MainWindow`

## Propósito
Gestiona el área MDI, menús, toolbars, docks y coordinación de viewports.

## Atributos

| Atributo | Descripción |
|----------|-------------|
| `mdi_area` | QMdiArea con viewports |
| `props_panel` | PropertiesPanel (dock derecho) |
| `scales_panel` | ScalesPanel (dock derecho) |
| `anim_toolbar` | AnimationToolbar |
| `pattern_combo` | QComboBox para filtrar patrones |
| `cmd_processor` | CommandProcessor |
| `console_widget` | CommandLineWidget |
| `file_menu` | FileMenu |
| `define_menu` | DefineMenu |
| `assign_menu` | AssignMenu |
| `analyze_menu` | AnalyzeMenu |
| `results_menu` | ResultsMenu (entre Analizar y Ver) |
| `tools_menu` | ToolsMenu |

## Handlers de Comandos CLI

| Handler | Comando asociado |
|---------|-----------------|
| `set_nodes_visible(visible)` | `show/hide nodes` |
| `set_elements_visible(visible)` | `show/hide elements` |
| `set_hinges_visible(visible)` | `show/hide hinges` |
| `set_crosses_visible(visible)` | `show/hide crosses` |
| `set_visibility(what, visible)` | Diagramas, deformada |
| `show_force_diagrams(type_)` | `show/hide diagrams M/V/P` |

## Funciones

| Función | Descripción |
|--------|-------------|
| `add_new_viewport()` | Crea nuevo viewport MDI |
| `add_tool_window()` | Añade ventana MDI genérica |
| `refresh_project()` | Emite dataChanged |
| `_refresh_pattern_combo()` | Actualiza combobox de patrones |
| `_on_pattern_selected()` | Propaga patrón a viewports |
| `broadcast_results()` | Envía resultados a todos los viewports |
| `set_pushover_loads_visible()` | Toggle cargas pushover |
| `toggle_animation_toolbar()` | Muestra/oculta barra de animación |
| `sync_animation_step()` | Sincroniza paso con todos los hijos |
| `execute_command()` | Procesa comando CLI |

## propiedades

| Propiedad | Descripción | Retorna |
|----------|-------------|---------|
| `_viewports` | Lista de StructureInteractor activos | list |
| `viz_widget` | Viewport activo | StructureInteractor |

## Conexiones

```
MainWindow
├── ProjectManager.dataChanged ──► refresh_project()
├── ProjectManager.dataChanged ──► _refresh_pattern_combo()
├── UnitManager.unitsChanged ──► refresh_project()
├── props_panel.dataChanged ──► refresh_project()
├── console_widget.commandEntered ──► execute_command()
├── pattern_combo ──► _on_pattern_selected()
```

## Relaciones

```
MainWindow
├── Menus ──► Instancia y contiene
├── Dialogs ──► Abre con exec()
├── StructureInteractor ──► Crea viewports
├── PropertiesPanel ──► Dock
├── ScalesPanel ──► Dock
├── AnimationToolbar ──► Toolbar
├── ProjectManager ──► Emite/escucha señales
└── CommandProcessor ──► Procesa comandos
```

## Relacionado Con

- [[ProjectManager]] - Gestor central
- [[Menus]] - Barras de menú
- [[Dialogs]] - Diálogos abiertos
- [[StructureInteractor]] - Viewport
- [[AnimationToolbar]] - Barra de animación
- [[ResultsMenu]] - Menú de resultados (entre Analizar y Ver)