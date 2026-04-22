# StructureInteractor

Widget central de visualización del modelo estructural.

## Clase
`StructureInteractor`

## Propósito
Viewport principal que usa pyqtgraph para renderizar el modelo, cargas, deformaciones y diagramas de fuerza.

## Señales

| Señal | Descripción |
|-------|-------------|
| `nodeSelected(node)` | Nodo seleccionado |
| `elementSelected(element)` | Elemento seleccionado |
| `selectionCleared()` | Selección limpiada |

## Atributos

| Atributo | Descripción |
|----------|-------------|
| `plot_widget` | PlotWidget de pyqtgraph |
| `renderer_model` | ModelRenderer |
| `renderer_load` | LoadRenderer |
| `renderer_deform` | DeformationRenderer |
| `renderer_forces` | ForceDiagramRenderer |
| `renderer_yield` | YieldRenderer |
| `current_results` | Resultados actuales (deformación) |
| `show_node_labels` | Toggle etiquetas de nodos |
| `show_element_labels` | Toggle etiquetas de elementos |
| `show_deformed` | Toggle deformación |
| `show_diagrams` | Toggle diagramas M/V/P |
| `show_pushover_loads` | Toggle cargas pushover |
| `active_pattern_tag` | Filtrar por patrón (None = todos) |

## Funciones

| Función | Descripción |
|--------|-------------|
| `refresh_viz()` | Redibuja toda la visualización |
| `_on_data_changed()` | Slot para dataChanged signal |
| `set_overlay_widget()` | Añade widget superpuesto |
| `set_active_pattern()` | Filtra cargas por patrón |
| `set_visibility()` | Toggle visibilidad por tipo |
| `show_force_diagrams()` | Muestra diagrama M/V/P |
| `show_deformation()` | Muestra resultados de deformación |
| `draw_kinematic_step()` | Dibuja paso de animación |
| `draw_kinematic_forces_step()` | Dibuja fuerzas del paso |
| `draw_kinematic_yield_step()` | Dibuja fluencia del paso |
| `set_pushover_loads_visible()` | Muestra cargas pushover |
| `increase_load_scale()` / `decrease_load_scale()` | Ajusta escala de cargas |
| `increase_deform_scale()` / `decrease_deform_scale()` | Ajusta escala de deformación |
| `toggle_node_labels()` | Toggle etiquetas de nodos |
| `toggle_element_labels()` | Toggle etiquetas de elementos |

## Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl++` | Aumentar escala de cargas |
| `Ctrl+-` | Disminuir escala de cargas |
| `PgUp` | Aumentar escala de deformación |
| `PgDown` | Disminuir escala de deformación |

## Opciones de Visualización

```python
show_node_labels     # Etiquetas de nodos
show_element_labels # Etiquetas de elementos
show_loads_nodes     # Cargas nodales
show_loads_elements # Cargas elementales
show_deformed       # Forma deformada
show_diagrams       # Diagramas M/V/P
show_pushover_loads # Cargas pushover temporales
active_pattern_tag  # Filtrar por patrón (None = todos)
```

## Relaciones

```
StructureInteractor
├── MainWindow ──► Lo instancia en add_new_viewport()
├── ProjectManager ──► Conecta dataChanged
├── ScaleManager ──► Conecta scale_changed
├── Visualizers ──► Instancia renderizadores
├── PropertiesPanel ──► Recibe señales nodeSelected/elementSelected
└── AnimationToolbar ──► Llama métodos de kinematic
```

## Relacionado Con

- [[MainWindow]] - Ventana principal que lo contiene
- [[Visualizers]] - Renderizadores
- [[ScaleManager]] - Factores de escala
- [[ProjectManager]] - Fuente de datos