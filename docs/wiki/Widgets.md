# Widgets

Directorio `src/ui/widgets/` que contiene los widgets reutilizables de la UI.

## StructureInteractor

Viewport central para visualización del modelo.

**Clase:** `StructureInteractor`

**Señales:**

| Señal | Descripción |
|-------|-------------|
| `nodeSelected(node)` | Nodo seleccionado |
| `elementSelected(element)` | Elemento seleccionado |
| `selectionCleared()` | Selección limpiada |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `refresh_viz()` | Redibuja toda la visualización |
| `set_active_pattern()` | Filtra cargas por patrón |
| `set_visibility()` | Toggle visibilidad |
| `show_force_diagrams()` | Muestra diagrama M/V/P |
| `show_deformation()` | Muestra resultados de deformación |
| `draw_kinematic_step()` | Dibuja paso de animación |
| `set_pushover_loads_visible()` | Muestra cargas pushover |

**Atajos:** Ctrl++/-- (escala cargas), PgUp/PgDown (escala deformación)

**Relacionado:** [[Visualizers]], [[ScaleManager]], [[ProjectManager]]

---

## MainWindow

Ventana principal de la aplicación.

**Clase:** `MainWindow`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `add_new_viewport()` | Crea nuevo viewport MDI |
| `add_tool_window()` | Añade ventana MDI genérica |
| `refresh_project()` | Emite dataChanged |
| `broadcast_results()` | Envía resultados a todos los viewports |
| `execute_command()` | Procesa comando CLI |
| `sync_animation_step()` | Sincroniza paso de animación |
| `toggle_animation_toolbar()` | Muestra/oculta barra de animación |
| `set_pushover_loads_visible()` | Toggle cargas pushover |

**Relacionado:** [[ProjectManager]], [[Menus]], [[Dialogs]], [[AnimationToolbar]]

---

## PropertiesPanel

Dock que muestra propiedades del elemento/nodo seleccionado.

**Clase:** `PropertiesPanel`

**Señales:**

| Señal | Descripción |
|-------|-------------|
| `dataChanged` | Datos modificados |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `show_node()` | Muestra formulario de nodo |
| `show_element()` | Muestra formulario de elemento |
| `clear_selection()` | Muestra placeholder |

**Relacionado:** [[ProjectManager]], [[StructureInteractor]]

---

## AnimationToolbar → [[AnimationToolbar]]

Barra de herramientas para animación paso a paso de resultados pushover.

**Clase:** `AnimationToolbar(QToolBar)`

**Controles:**
- `step_label` — etiqueta con el paso actual
- `step_slider` — `QSlider` horizontal (deshabilitado hasta que haya resultados)
- `chk_sync` — checkbox "Sincronizar gráficas" (sincroniza con `MomentCurvatureWidget` si está abierto)

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `load_pushover_results()` | Lee `manager.pushover_results["node_displacements"]`, fija el máximo del slider y lo habilita; retorna `bool` |
| `_on_slider_changed(value)` | Extrae `step_data`, `step_forces`, `step_yield`, `step_frozen`, `frozen_columns` del paso `value`; llama `draw_kinematic_step` + `draw_kinematic_yield_step` en el viewport activo; delega sincronización a `parent_window.sync_animation_step()` |

**Relacionado:** [[ProjectManager]], [[MainWindow]], [[StructureInteractor]]

---

## ScalesPanel → [[ScalesPanel]]

Panel dock para ajustar multiplicadores de escala visual de renderizado.

**Clase:** `ScalesPanel`

**Grupos de Controles:**

| Grupo | Control | Tipo Scale |
|------|---------|-----------|
| Visualización General | Tamaño de Nodos | `node_size` |
| | Escala de Cargas | `load` |
| | Deformada | `deformation` |
| Diagramas de Fuerzas | Momento M | `moment` |
| | Cortante V | `shear` |
| | Axial P | `axial` |

**Rango de spinboxes:** 0.1 - 100.0 (step 0.25)

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `_create_spinbox()` | Crea QDoubleSpinBox con rango y step |
| `_update_all_spinboxes()` | Sincroniza UI con ScaleManager |
| `_on_spinbox_changed()` | Envía cambio al ScaleManager |
| `_on_external_multiplier_changed()` | Actualiza UI sin re-emitir |

**Señales:**
- Se conecta a `ScaleManager.multiplier_changed` para actualizar desde código externo

**Relacionado:** [[ScaleManager]]

---

## UnitSpinBox → [[UnitSpinBox]]

Spinbox especializado que maneja conversión automática de unidades.

**Clase:** `UnitSpinBox(QDoubleSpinBox)`

**Atributos:**

| Atributo | Descripción |
|----------|-------------|
| `_base_value` | Valor interno en unidades canónicas (SI) |
| `unit_type` | Tipo de unidad (UnitType) |

**Señales:**
- Se conecta a `UnitManager.unitsChanged` para actualizar suffix

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `_on_value_changed_internal()` | Recalcula valor base al cambiar valor visual |
| `_update_display()` | Actualiza suffix y ajusta valor según unidad actual |
| `get_value_base()` | Retorna valor en unidades canónicas (m, kN, etc.) |
| `set_value_base()` | Establece valor desde unidades canónicas |
| `validate()` | Validación de texto |

**Comportamiento:**
- Cuando el usuario escribe "300" con unidad "mm", internamente guarda 0.3 (metros)
- Al cambiar a unidad "cm", muestra "30" automáticamente

**Relacionado:** [[UnitManager]]

---

## SectionPreview → [[SectionPreview]]

Widget que previsualiza secciones de fibra (hereda de `pg.PlotWidget`).

**Clase:** `SectionPreview(pg.PlotWidget)`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `_setup_ui()` | Crea ítems gráficos: contorno (concreto), barras (acero), flechas de ejes Y/Z |
| `plot_section(fiber_section)` | Dibuja patches de hormigón y capas de barras; ajusta flechas de ejes dinámicamente |

**Elementos gráficos:**
- `concrete_outline` — `PlotDataItem` con contorno de patches (negro)
- `steel_bars` — `ScatterPlotItem` en `pxMode=False` (tamaño en metros, rojo)
- `arrow_y` / `arrow_z` — `ArrowItem` para ejes locales Y (azul) / Z (verde)
- `label_y` / `label_z` — etiquetas de ejes

**Relacionado:** [[Sections]], [[SectionDialog]]

---

## SectionForm / AggregatorForm → [[SectionForms]]

Formularios para creación de secciones.

**Clases:** `SectionForm`, `AggregatorForm`

### SectionForm

Formulario para sección de fibra rectangular con refuerzo en 4 caras.

| Función | Descripción |
|--------|-------------|
| `populate_materials()` | Pobla combos de `Concrete01` y `Steel01` desde el manager |
| `get_data()` | Retorna dict con: nombre, b, h, materiales, recubrimiento, barras (qty+diam) por cara, subdivisión nIy/nIz |
| `set_data(section)` | Reconstruye formulario desde `FiberSection`: detecta patches para b/h, layers por posición geométrica |

**Campos:**
- Nombre, base (b), altura (h), material concreto, material acero, recubrimiento
- Refuerzo: superior, inferior, izquierdo, derecho (cantidad + diámetro)
- Discretización: nIy, nIz (subdivisiones de patch)

### AggregatorForm

Formulario para `SectionAggregator` (sección base + materiales por DOF).

| Función | Descripción |
|--------|-------------|
| `populate(manager)` | Pobla combo de secciones base (`FiberSection`) y materiales |
| `add_aggregation()` | Añade par (material, DOF) validando no repetir DOF |
| `del_aggregation()` | Elimina par seleccionado |
| `refresh_list()` | Actualiza `QListWidget` con las agregaciones actuales |
| `get_data()` | Retorna dict con nombre, `base_section_tag`, lista de `{mat_tag, dof}` |
| `set_data(section, manager)` | Reconstruye formulario desde `SectionAggregator` |

**DOFs disponibles:** Vy, P, Mz

**Relacionado:** [[Sections]], [[Materials]]

---

## MaterialForms → [[MaterialForms]]

Formularios para creación de materiales. Cada clase implementa `get_data()` y `set_data(material)`.

**Clases:** `ConcreteForm`, `SteelForm`, `ElasticForm`, `HystereticForm`, `HystereticSMForm`

### ConcreteForm — Concrete01

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `spin_rho_c` | UnitSpinBox(DENSITY) | Densidad (default 2500 kg/m³) |
| `spin_fpc` | UnitSpinBox(STRESS) | Resistencia a compresión (default 25 MPa) |
| `spin_epsc0` | QDoubleSpinBox | Deformación pico (default 0.002) |
| `spin_fpcU` | UnitSpinBox(STRESS) | Resistencia al aplastamiento |
| `spin_epscU` | QDoubleSpinBox | Deformación última (default 0.0035) |
| Opcionales | - | Envolvente MinMax (min/max strain) |

### SteelForm — Steel01

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `spin_rho_s` | UnitSpinBox(DENSITY) | Densidad (default 7850 kg/m³) |
| `spin_Fy` | UnitSpinBox(STRESS) | Esfuerzo de fluencia (default 500 MPa) |
| `spin_E0` | UnitSpinBox(STRESS) | Módulo elástico (default 200 GPa) |
| `spin_b` | QDoubleSpinBox | Ratio de endurecimiento |
| Opcionales | - | a1–a4 (endurecimiento isotrópico), MinMax |

### ElasticForm — Elastic

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `spin_rho` | UnitSpinBox(DENSITY) | Densidad |
| `spin_E` | UnitSpinBox(STRESS) | Módulo elástico |

### HystereticForm — Hysteretic

Tres tabs: **Env. Positiva (+)**, **Env. Negativa (-)**, **Histéresis**.
- 3 puntos (s, e) por envolvente (esfuerzo en UnitSpinBox(STRESS))
- pinch_x, pinch_y, damage1, damage2, beta (opcional)
- Gráfica Matplotlib embebida que se actualiza en tiempo real

### HystereticSMForm — HystereticSM

Igual que `HystereticForm` pero con **4 puntos** por envolvente y unidades en `UnitType.MOMENT` (para leyes momento-curvatura).

**Relacionado:** [[Materials]]

---

## PropertiesForms → [[PropertiesForms]]

Formularios para editar propiedades de nodos y elementos en el `PropertiesPanel`.

**Clases:** `NodeForms`, `ElementForm`

### NodeForms

| Función | Descripción |
|--------|-------------|
| `load_node(node)` | Rellena formulario con datos del nodo (coords, fixity, masa) |
| `apply_changes()` | Guarda cambios en el nodo y emite `dataChanged` |
| `_on_value_changed()` | Habilita botón "Aplicar" al detectar cambio |

**Señales:** `dataChanged`

**Campos:** Tag (read-only), X, Y (`UnitSpinBox(LENGTH)`), restricciones (fix_x, fix_y, fix_rz), masa nodal opcional (mx, my, mrz en `UnitSpinBox(MASS)`)

### ElementForm

| Función | Descripción |
|--------|-------------|
| `load_element(element)` | Rellena formulario; muestra bloque hinge si es `ForceBeamColumnHinge` |
| `apply_changes()` | Guarda cambios; llama `mark_topology_dirty()` si cambian nodos |
| `_on_value_changed()` | Habilita botón "Aplicar" |

**Señales:** `dataChanged`

**Campos:** Tag (read-only), nodo_i, nodo_j, sección (combo). Para `ForceBeamColumnHinge`: sección_i, sección_j, Lp_i, Lp_j adicionales.

**Relacionado:** [[Node]], [[Element]]

---

## CommandLineWidget → [[CommandLineWidget]]

Barra de entrada de comandos CLI con historial y selector de unidades.

**Clases:** `HistoryLineEdit(QLineEdit)`, `CommandLineWidget(QWidget)`

### HistoryLineEdit

`QLineEdit` con navegación por historial mediante flechas ↑↓.

| Función | Descripción |
|--------|-------------|
| `keyPressEvent(event)` | Navega por historial con Up/Down; resto delega a QLineEdit |
| `add_history(text)` | Añade texto al historial (máx. 100 entradas) |

### CommandLineWidget

| Función | Descripción |
|--------|-------------|
| `_on_enter()` | Emite `commandEntered`, añade al historial, limpia input |
| `log_message(message, color, bold)` | Imprime a stdout con prefijo `[INFO]`/`[ERROR]` |

**Señales:** `commandEntered(str)`

**Layout:** `HistoryLineEdit` (stretch=1) + `UnitSelectorWidget` (stretch=0), altura fija 40px

**Relacionado:** [[CommandProcessor]], [[UnitManager]]

---

## UnitSelectorWidget → [[UnitSelectorWidget]]

Combo de presets de unidades embebido en la barra de comandos.

**Clase:** `UnitSelectorWidget(QComboBox)`

**Presets disponibles:**

| Label | FORCE | LENGTH | SECTION_DIM | MOMENT | STRESS | DIST_FORCE |
|-------|-------|--------|-------------|--------|--------|------------|
| kN, m | kN | m | mm | kNm | MPa | kN/m |
| N, mm | N | mm | mm | Nm | MPa | N/mm |
| Ton, m | Ton | m | m | Ton-m | — | Ton/m |
| kips, ft | kips | ft | in | kip-ft | ksi | kips/ft |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `_apply_preset(index)` | Aplica el preset al `UnitManager`; bloquea señales de `um` durante la iteración y emite `unitsChanged` al final (evita N refrescos) |

**Relacionado:** [[UnitManager]], [[CommandLineWidget]]

---

## CommandConsole → [[CommandConsole]]

Widget combinado de entrada + salida de comandos CLI (con área de texto de log).

**Clase:** `CommandConsole(QWidget)`

**Señales:**

| Señal | Descripción |
|-------|-------------|
| `commandEntered(str)` | Emite comando cuando el usuario pulsa Enter |

**Atributos:**
- `history` — lista de comandos anteriores
- `history_index` — posición en el historial

**Relacionado:** [[CommandProcessor]]

---

## Relaciones

```
Widgets
├── MainWindow ──► Los contiene/organiza
├── ProjectManager ──► Acceden a datos
├── ScaleManager ──► Usan escalas
├── UnitManager ──► Usan/convierten unidades
└── Visualizers ──►usan widgets de viewport
```

## Relacionado Con

- [[MainWindow]] - Ventana principal
- [[Visualizers]] - Renderizadores
- [[ScaleManager]] - Gestor de escalas
- [[UnitManager]] - Gestor de unidades