# Menus

Directorio `src/ui/menus/` que contiene los menús de la barra de menú principal.

## FileMenu → [[FileMenu]]

Menú de archivo para operaciones de proyecto.

**Clase:** `FileMenu`

**Acciones del menú:**

| Acción | Atajo | Descripción |
|--------|-------|-------------|
| "Nuevo Proyecto" | — | Llama `manager.new_project()` |
| "Cargar Proyecto" | — | Abre `QFileDialog` y llama `manager.load_project()` |
| "Guardar Proyecto" | — | Abre `QFileDialog` y llama `manager.save_project()` |
| "Salir" | — | `QApplication.instance().quit()` |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `setup_actions()` | Crea y conecta las cuatro acciones |
| `open_new_project()` | Llama `ProjectManager.new_project()` |
| `open_load_dialog()` | Abre `QFileDialog` para JSON y llama `load_project()` |
| `open_save_dialog()` | Abre `QFileDialog` para JSON y llama `save_project()` |

**Relacionado:** [[ProjectManager]]

---

## DefineMenu → [[DefineMenu]]

Menú para definir elementos del modelo.

**Clase:** `DefineMenu`

**Acciones del menú:**

| Acción | Función conectada | Descripción |
|--------|------------------|-------------|
| "Materiales" | `open_material_dialog()` | Abre `MaterialDialog` |
| "Secciones" | `open_section_dialog()` | Abre `SectionDialog` |
| "Geometría Libre (Nodos/Elementos)" | `open_geometry_dialog()` | Abre `GeometryDialog` |
| "Patrones de Carga" | `open_pattern_dialog()` | Abre `PatternDialog` |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `setup_actions()` | Crea y conecta las cuatro acciones |
| `open_material_dialog()` | Instancia y ejecuta `MaterialDialog` |
| `open_section_dialog()` | Instancia y ejecuta `SectionDialog` |
| `open_geometry_dialog()` | Instancia y ejecuta `GeometryDialog` |
| `open_pattern_dialog()` | Instancia y ejecuta `PatternDialog` |

**Relacionado:** [[MaterialDialog]], [[SectionDialog]], [[GeometryDialog]], [[PatternDialog]]

---

## AssignMenu → [[AssignMenu]]

Menú para asignar cargas y restricciones.

**Clase:** `AssignMenu`

**Acciones del menú:**

| Acción | Función conectada | Descripción |
|--------|------------------|-------------|
| "Restricciones" | `open_restraints()` | Abre `RestraintsDialog` |
| "Cargas en los nodos" | `open_nodal_loads()` | Abre `NodalLoadsDialog` |
| "Cargas en los elementos" | `open_element_loads()` | Abre `ElementLoadsDialog` |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `open_restraints()` | Instancia y ejecuta `RestraintsDialog` |
| `open_nodal_loads()` | Instancia y ejecuta `NodalLoadsDialog` |
| `open_element_loads()` | Instancia y ejecuta `ElementLoadsDialog` |

**Relacionado:** [[NodalLoadsDialog]], [[ElementLoadsDialog]], [[RestraintsDialog]]

---

## AnalyzeMenu → [[AnalyzeMenu]]

Menú para ejecutar análisis.

**Clase:** `AnalyzeMenu`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `run_gravity()` | Construye modelo + análisis de gravedad; guarda `gravity_results` y llama `broadcast_results()` (atajo F5) |
| `run_modal()` | Ejecuta `translator.run_modal_analysis(1)` |
| `show_pushover_dialog()` | Verifica que existan `gravity_results`; si no, ofrece ejecutarlos; luego abre `PushoverDialog` |
| `_show_diagram(type_)` | Llama `viz_widget.show_force_diagrams(type_)` con "M", "V" o "P" |
| `_set_deformed_visibility(visible)` | Llama `viz_widget.set_visibility("deformed", visible)` |
| `_clear_results()` | Oculta diagramas y deformada en todos los viewports |
| `_show_curve_pushover()` | Abre `PushoverResultsWidget` en ventana MDI con los `pushover_results` |
| `_show_section_results()` | Abre `MomentCurvatureWidget` en ventana MDI |

**Relacionado:** [[OpenSeesTranslator]], [[PushoverDialog]]

---

## ToolsMenu → [[ToolsMenu]]

Menú de herramientas para generación automática de modelos y cargas.

**Clase:** `ToolsMenu`

**Acciones del menú:**

| Acción | Submenú | Función conectada | Descripción |
|--------|---------|------------------|-------------|
| "Generar Pórtico 2D" | — | `show_grid_dialog()` | Abre `GridDialog` y llama `FrameGenerator` |
| "Generar Peso Propio" | Generación de Cargas | `open_self_weight_dialog()` | Abre `SelfWeightDialog` |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `show_grid_dialog()` | Abre `GridDialog`; si el usuario acepta, llama `FrameGenerator.generate_2d_frame()` con los datos y refresca el viewport |
| `open_self_weight_dialog()` | Instancia y ejecuta `SelfWeightDialog` |

**Relacionado:** [[GridDialog]], [[SelfWeightDialog]], [[FrameGenerator]]

## Relaciones

```
Menus
├── MainWindow ──► Los contiene
├── Dialogs ──► Abren diálogos
├── ProjectManager ──► Manipulan datos
└── OpenSeesTranslator ──► Ejecutan análisis
```

## Relacionado Con

- [[MainWindow]] - Ventana principal
- [[Dialogs]] - Diálogos abiertos por menús