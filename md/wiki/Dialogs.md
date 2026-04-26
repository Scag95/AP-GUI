# Dialogs

Directorio `src/ui/dialogs/` que contiene los diálogos modales de la aplicación.

## MaterialDialog → [[MaterialDialog]]

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

## SectionDialog → [[SectionDialog]]

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

## GeometryDialog → [[GeometryDialog]]

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

## PatternDialog → [[PatternDialog]]

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

## NodalLoadsDialog → [[NodalLoadsDialog]]

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

## ElementLoadsDialog → [[ElementLoadsDialog]]

Diálogo para asignar cargas distribuidas uniformes a elementos de barra.

**Clase:** `ElementLoadsDialog`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `populate_patterns()` | Pobla combo con patrones disponibles |
| `populate_elements()` | Lista elementos (opcionalmente solo con carga) |
| `select_from_text()` | Selecciona en la lista los IDs escritos en el campo de texto |
| `_parse_input(text)` | Convierte "1,3-5" en lista de IDs |
| `apply_loads()` | Crea/reemplaza `ElementLoad` en elementos seleccionados |
| `clear_loads()` | Elimina cargas de elementos seleccionados |
| `_remove_load_for_element(element_tag)` | Borra la carga de un elemento del patrón activo |
| `on_element_selected()` | Rellena spinboxes wx/wy al seleccionar en la lista |
| `toggle_tags(checked)` | Muestra/oculta etiquetas de elementos en el viewport |

**Controles:**
- Texto "Elementos (coma/rangos)": selección por ID
- `chk_assigned_only`: filtra lista a solo los que tienen carga
- `chk_show_tags`: toggle de etiquetas en el viewport
- Selector de patrón de carga destino
- `UnitSpinBox` wx y wy (tipo `DISTRIBUTED_FORCE`)

**Relacionado:** [[ElementLoad]], [[LoadPattern]]

---

## PushoverDialog → [[PushoverDialog]]

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

## PushoverResultsWidget → [[PushoverResultsWidget]]

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

## FiberStrainDialog → [[FiberStrainDialog]]

Widget MDI (anclable) para visualizar la sección transversal de fibras coloreada por strain en cada paso del pushover.

**Clase:** `FiberStrainDialog(QWidget)`  
**Archivo:** `src/ui/dialogs/fiber_strain_dialog.py`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `_rebuild_section()` | Reconstruye la escena al cambiar elemento o punto de integración |
| `_build_shapes(sec)` | Crea rectángulos de fibras y puntos de barras de acero usando definición de sección (outer=nIz, inner=nIy) |
| `_compute_global_scale()` | Calcula escala simétrica global `±amp` sobre todos los pasos |
| `_setup_labels()` | Crea `pg.TextItem` por fibra para mostrar el valor de strain |
| `_update_colors()` | Actualiza colores de fibras y labels para el paso actual |
| `_fiber_color(strain, fiber_idx)` | Retorna color EC8 (DL/SL/NC) o gradiente azul-blanco-rojo |
| `_strain_color(strain, vmin, vmax)` | Interpolación lineal de color en escala fría-caliente |
| `connect_to_animation(anim_toolbar)` | Conecta slider propio al `step_slider` del `AnimationToolbar` |
| `_on_main_step(value)` | Sincroniza slider local cuando cambia el slider del AnimationToolbar |

**Controles:**
- Selector de elemento (ForceBeamColumn / ForceBeamColumnHinge)
- Selector de punto de integración
- Slider de paso
- Vista `pg.PlotWidget` con `_PatchItem` (rectángulos de fibras) + `pg.ScatterPlotItem` (barras de acero) + `pg.TextItem` (labels de strain)

**Criterios de color EC8:**
- Steel01: `ε ≥ Fy/E0` → amarillo (DL)
- Concrete01: `ε ≥ 0.75×εcu` → naranja (SL), `ε ≥ 1.25×εcu` → rojo (NC)
- Resto: gradiente azul-blanco-rojo según escala global simétrica

**Nota técnica:** `fiberData` devuelve `z=0` en análisis 2D, por lo que las posiciones se extraen de la definición de sección (`patch.zI + (c+0.5)*dz`), no de las coordenadas de OpenSees.

**Relacionado:** [[ProjectManager]], [[FiberSection]], [[AnimationToolbar]], [[AnalyzeMenu]]

---

## MomentCurvatureWidget → [[MomentCurvatureWidget]]

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

## RestraintsDialog → [[RestraintsDialog]]

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

## SelfWeightDialog → [[SelfWeightDialog]]

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

## GridDialog → [[GridDialog]]

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
├── AnalyzeMenu ──► Abre PushoverDialog, FiberStrainDialog
└── OpenSeesTranslator ──► Ejecuta análisis
```

## Relacionado Con

- [[MainWindow]] - Ventana principal
- [[Menus]] - Menús que abren diálogos
- [[ProjectManager]] - Almacena datos