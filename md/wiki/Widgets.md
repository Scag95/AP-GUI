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

## AnimationToolbar

Barra de herramientas para animación de resultados pushover.

**Clase:** `AnimationToolbar`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `load_pushover_results()` | Carga resultados al slider |
| `_on_slider_changed()` | Sincroniza todos los viewports |

**Relacionado:** [[ProjectManager]], [[MainWindow]]

---

## ScalesPanel

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

## UnitSpinBox

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

## SectionPreview

Widget que previsualiza secciones de fibra.

**Clase:** `SectionPreview`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `plot_section()` | Dibuja sección |

**Relacionado:** [[Sections]]

---

## SectionForm / AggregatorForm

Formularios para creación de secciones.

**Clases:** `SectionForm`, `AggregatorForm`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `get_data()` | Retorna datos del formulario |
| `set_data()` | Rellena formulario |
| `populate_materials()` | Pobla combos de materiales |

**Relacionado:** [[Sections]], [[Materials]]

---

## MaterialForms

Formularios para creación de materiales.

**Clases:** `ConcreteForm`, `SteelForm`, `ElasticForm`, `HystereticForm`, `HystereticSMForm`

**Relacionado:** [[Materials]]

---

## PropertiesForms

Formularios para editar propiedades de nodos y elementos.

**Clases:** `NodeForms`, `ElementForm`

**Relacionado:** [[Node]], [[Element]]

---

## CommandLineWidget

Widget de consola de comandos CLI.

**Clase:** `CommandLineWidget`

**Señales:**

| Señal | Descripción |
|-------|-------------|
| `commandEntered` | Comando ingresado |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `log_message()` | Registra mensaje |

**Relacionado:** [[CommandProcessor]], [[UnitManager]]

---

## UnitSelectorWidget

Widget selector de unidad con presets predefinidos.

**Clase:** `UnitSelectorWidget`

**Presets:**
- kN, m
- N, mm
- Ton, m
- kips, ft

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `_apply_preset()` | Aplica preset seleccionado al UnitManager |

**Relacionado:** [[UnitManager]]

---

## CommandConsole

Widget de consola de comandos CLI.

**Clase:** `CommandConsole`

**Señales:**

| Señal | Descripción |
|-------|-------------|
| `commandEntered` | Emite comando ingresado |

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