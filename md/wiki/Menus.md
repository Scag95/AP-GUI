# Menus

Directorio `src/ui/menus/` que contiene los menús de la barra de menú principal.

## FileMenu

Menú de archivo para operaciones de proyecto.

**Clase:** `FileMenu`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `open_new_project()` | Crea nuevo proyecto |
| `open_load_dialog()` | Abre archivo JSON |
| `open_save_dialog()` | Guarda archivo JSON |

**Relacionado:** [[ProjectManager]]

---

## DefineMenu

Menú para definir elementos del modelo.

**Clase:** `DefineMenu`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `open_material_dialog()` | Abre MaterialDialog |
| `open_section_dialog()` | Abre SectionDialog |
| `open_geometry_dialog()` | Abre GeometryDialog |
| `open_pattern_dialog()` | Abre PatternDialog |

**Relacionado:** [[MaterialDialog]], [[SectionDialog]], [[GeometryDialog]], [[PatternDialog]]

---

## AssignMenu

Menú para asignar cargas y restricciones.

**Clase:** `AssignMenu`

**Relacionado:** [[NodalLoadsDialog]], [[ElementLoadsDialog]], [[RestraintsDialog]]

---

## AnalyzeMenu

Menú para ejecutar análisis.

**Clase:** `AnalyzeMenu`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `run_gravity()` | Ejecuta análisis de gravedad |
| `run_modal()` | Ejecuta análisis modal |
| `show_pushover_dialog()` | Abre PushoverDialog |
| `_show_diagram()` | Muestra diagrama M/V/P |
| `_set_deformed_visibility()` | Muestra/oculta deformada |
| `_clear_results()` | Limpia resultados |
| `_show_curve_pushover()` | Abre curva de capacidad |
| `_show_section_results()` | Abre análisis M-φ |

**Relacionado:** [[OpenSeesTranslator]], [[PushoverDialog]]

---

## ToolsMenu

Menú de herramientas.

**Clase:** `ToolsMenu`

**Relacionado:** [[CommandProcessor]]

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