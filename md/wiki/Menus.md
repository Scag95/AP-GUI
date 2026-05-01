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

**Nota:** Las acciones de visualización de resultados (diagramas, deformada, pushover, etc.) se encuentran en [[ResultsMenu]].

**Relacionado:** [[OpenSeesTranslator]], [[PushoverDialog]], [[ResultsMenu]]

---

## ResultsMenu → [[ResultsMenu]]

Menú para visualizar resultados del análisis. Se sitúa entre Analizar y Ver.

**Clase:** `ResultsMenu`

**Acciones del menú:**

| Acción | Función |
|-------|---------|
| Deformada | `_set_deformed_visibility(True)` |
| Momentos (M) | `_show_diagram("M")` |
| Cortantes (V) | `_show_diagram("V")` |
| Axiales (P) | `_show_diagram("P")` |
| Curva Pushover | `_show_curve_pushover()` |
| Análisis de Sección (M-φ) | `_show_section_results()` |
| Deformaciones de Fibras | `_show_fiber_strains()` |
| Ocultar Resultados | `_clear_results()` |

**Relacionado:** [[PushoverResultsWidget]], [[MomentCurvatureWidget]], [[FiberStrainDialog]]

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