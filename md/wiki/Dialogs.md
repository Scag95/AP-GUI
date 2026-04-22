# Dialogs

Directorio `src/ui/dialogs/` que contiene los diálogos modales de la aplicación.

## MaterialDialog

Diálogo para definir materiales estructurales.

**Clase:** `MaterialDialog`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `__init__()` | Configura UI con stacked forms |
| `add_material()` | Crea material desde formulario |
| `delete_material()` | Elimina material seleccionado |
| `update_material()` | Actualiza material seleccionado |
| `load_materials()` | Carga lista de materiales |
| `on_material_selected()` | Rellena formulario al seleccionar |

**Tipos de Material:** Concrete01, Steel01, Elastic, Hysteretic, HystereticSM

**Relacionado:** [[Materials]], [[MaterialForms]]

---

## SectionDialog

Diálogo para crear y modificar secciones.

**Clase:** `SectionDialog`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `__init__()` | Configura UI con tabs y preview |
| `add_section()` | Crea sección desde formulario |
| `delete_section()` | Elimina sección |
| `update_section()` | Actualiza sección |
| `load_sections()` | Carga lista de secciones |
| `on_section_selected()` | Rellena formulario |
| `update_preview()` | Actualiza preview visual |
| `_build_section_from_form()` | Crea sección temporal |
| `_setup_section_geometry()` | Configura patches y layers |
| `on_tab_changed()` | Pobla combos al cambiar tab |

**Relacionado:** [[Sections]], [[SectionForms]], [[SectionPreview]]

---

## GeometryDialog

Diálogo para crear y modificar nodos y elementos.

**Clase:** `GeometryDialog`

**Funciones (Nodos):**

| Función | Descripción |
|--------|-------------|
| `setup_nodes_tab()` | Configura pestaña de nodos |
| `on_add_node_clicked()` | Crea nodo |
| `refresh_node_list()` | Actualiza lista |
| `on_node_selected()` | Rellena formulario |
| `delete_node()` | Elimina nodo |
| `update_node()` | Actualiza nodo |

**Funciones (Elementos):**

| Función | Descripción |
|--------|-------------|
| `setup_elements_tab()` | Configura pestaña de elementos |
| `load_data()` | Pobla combos y lista |
| `on_add_element_clicked()` | Crea elemento |
| `on_element_selected()` | Rellena formulario |
| `delete_element()` | Elimina elemento |
| `update_element()` | Actualiza elemento |
| `on_element_type_changed()` | Muestra/oculta opciones de bisagra |

**Relacionado:** [[Node]], [[Element]]

---

## PatternDialog

Gestor de patrones de carga.

**Clase:** `PatternDialog`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `load_patterns()` | Carga lista de patrones |
| `on_pattern_selected()` | Rellena formulario |
| `add_pattern()` | Crea patrón |
| `update_pattern()` | Actualiza patrón |
| `delete_pattern()` | Elimina patrón |

**Relacionado:** [[Loads]], [[LoadPattern]]

---

## NodalLoadsDialog

Diálogo para asignar cargas nodales.

**Clase:** `NodalLoadsDialog`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `populate_patterns()` | Pobla selector de patrones |
| `populate_nodes()` | Pobla lista de nodos |
| `select_from_text()` | Selecciona nodos por texto |
| `apply_loads()` | Aplica cargas a nodos |
| `clear_loads()` | Elimina cargas |
| `_parse_input()` | Parsea rangos "1,2,5-9" |
| `on_node_selected()` | Rellena campos de fuerza |

**Relacionado:** [[NodalLoad]], [[LoadPattern]]

---

## ElementLoadsDialog

Diálogo para asignar cargas distribuidas a elementos.

**Clase:** `ElementLoadsDialog`

**Relacionado:** [[ElementLoad]]

---

## PushoverDialog

Diálogo de configuración para análisis pushover.

**Clase:** `PushoverDialog`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `populate_nodes()` | Pobla selector de nodos |
| `_on_load_type_changed()` | Muestra/oculta selector de patrón |
| `run_pushover()` | Ejecuta análisis |

**Parámetros:**
- Nodo de control
- Desplazamiento máximo
- Número de pasos
- Tipo de patrón (Modal, Uniforme, Patrón Definido)
- Análisis adaptativo
- Criterios de fallo personalizados

**Relacionado:** [[PushoverSolver]], [[OpenSeesTranslator]]

---

## PushoverResultsWidget

Widget para visualizar curvas de capacidad pushover.

**Clase:** `PushoverResultsWidget`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `_on_toggle_loads()` | Toggle visualización de fuerzas pushover en 3D |
| `_on_slider_changed()` | Actualiza gráfico según paso seleccionado |
| `update_plot()` | Dibuja curvas global y por planta |
| `_draw_limit_state_markers()` | Dibuja marcadores de estados límite (DL/SL/NC) |

**Datos soportados:**
- Curva global (Base Shear vs Roof Drift)
- Curvas por planta
- Identificación de ciclos (pushover adaptativo)

**Estados límite:** DL (Service), SL (Safety), NC (Collapse)

**Relacionado:** [[Solvers]], [[ProjectManager]], [[ScaleManager]]

---

## MomentCurvatureWidget

Widget para análisis momento-curvatura de elementos.

**Clase:** `MomentCurvatureWidget`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `load_available_elements()` | Busca archivos `ele_*_force.out` en `pushover_data/` |
| `_on_element_changed()` | Carga datos del elemento seleccionado |
| `load_element_data()` | Parsea archivos `.out` de fuerzas y deformaciones |
| `update_plot()` | Grafica curvas M-φ con conversión de unidades |

**Controles:**
- Selector de elemento
- Selector de variable eje Y (Momento, Axial, Cortante)
- Lista de secciones (checkboxes)
- Slider para animar pasos

**Relacionado:** [[Element]], [[ProjectManager]]

---

## RestraintsDialog

Diálogo para definir restricciones nodales (soportes).

**Clase:** `RestraintsDialog`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `_quick_select()` | Selecciona todos o borde inferior |
| `_parse_node_input()` | Parsea "1,2,5-9" a lista de IDs |
| `_on_apply()` | Aplica fixity a nodos seleccionados |
| `_on_remove()` | Quita restricciones de nodos seleccionados |
| `_refresh_list()` | Actualiza lista de nodos restringidos |

**DOF disponibles:** UX, UY, RZ

**Relacionado:** [[Node]]

---

## SelfWeightDialog

Diálogo para aplicar peso propio a elementos.

**Clase:** `SelfWeightDialog`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `populate_patterns()` | Pobla combo con patrones de carga |
| `generate_loads()` | Genera cargas de peso propio |
| `apply_self_weight()` | Calcula y añade cargas basadas en densidad |

**Opciones:**
- Patrón destino
- Aplicar solo a vigas (horizontales)
- Reemplazar cargas distribuidas existentes

**Relacionado:** [[Loads]], [[ElementLoad]]

---

## GridDialog

Diálogo para generar mallas de nodos/elementos.

**Clase:** `gridDialog`

**Parámetros:**
- Número de pisos y vanos
- Altura de entrepisos, ancho de vano
- Puntos de integración (3-10)
- Sección de columnas y vigas
- Checkbox para generar vigas en base

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `populate_sections()` | Pobla combos con secciones disponibles |
| `get_data()` | Retorna diccionario con configuración |

**Relacionado:** [[FrameGenerator]]

---

## Relaciones

```
Dialogs
├── MainWindow ──► Los abre
├── ProjectManager ──► Almacenan/leer datos
├── DefineMenu ──► Abre MaterialDialog, SectionDialog, etc.
├── AssignMenu ──► Abre NodalLoadsDialog, ElementLoadsDialog, etc.
├── AnalyzeMenu ──► Abre PushoverDialog
└── OpenSeesTranslator ──► Ejecuta análisis
```

## Relacionado Con

- [[MainWindow]] - Ventana principal
- [[Menus]] - Menús que abren diálogos
- [[ProjectManager]] - Almacena datos