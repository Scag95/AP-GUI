# Visualizers

Directorio `src/ui/visualizers/` que contiene los renderizadores gráficos.

## Arquitectura

```
StructureInteractor
├── ModelRenderer      → Nodos y elementos
├── LoadRenderer       → Flechas de carga
├── DeformationRenderer → Forma deformada
├── ForceDiagramRenderer → Diagramas M/V/P
└── YieldRenderer      → Estado de fluencia
```

## ModelRenderer → [[ModelRenderer]]

Dibuja la estructura básica: nodos y elementos.

**Clase:** `ModelRenderer`

**Atributos:**

| Atributo | Descripción |
|----------|-------------|
| `scatter_nodes` | `ScatterPlotItem` único para todos los nodos (eficiencia) |
| `element_items` | `{ele_tag: PlotCurveItem}` — líneas de elementos |
| `labels` | Lista de `TextItem` de etiquetas |
| `pen_element` | `QPen` negro ancho 2 para barras |
| `brush_node` | `QBrush` azul `#2196F3` para nodos libres |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `attach(plot_widget)` | Añade `scatter_nodes` al plot (llamar una sola vez) |
| `clear(plot_widget)` | Elimina líneas y etiquetas; vacía el scatter |
| `draw_structure(plot_widget, manager, show_node_labels, show_element_labels, on_element_click)` | Dibuja elementos como líneas clickables y nodos con símbolo según fixity |
| `highlight_node(node_tag, color)` | Resaltado de nodo (pendiente de implementar) |

**Símbolos de nodo según fixity:**

| Fixity | Símbolo | Color |
|--------|---------|-------|
| `[0,0,0]` libre | `o` (círculo) | Azul `#2196F3` |
| `[1,1,1]` empotrado | `s` (cuadrado) | Rojo `#D32F2F` |
| `[1,1,0]` articulado | `t1` (triángulo) | Verde `#4CAF50` |
| `[0,1,0]`/`[1,0,0]` rodillo | `o` | Amarillo `#FFC107` |

Tamaño de nodo obtenido de `ScaleManager.get_scale('node_size')`.

**Señales:** `curve.sigClicked` → `on_element_click` callback con `curve.ele_tag`

**Relacionado:** [[ScaleManager]], [[ProjectManager]]

---

## LoadRenderer → [[LoadRenderer]]

Dibuja flechas de carga nodales y distribuidas.

**Clase:** `LoadRenderer`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `clear(plot_widget)` | Elimina todos los ítems de carga del plot |
| `draw_loads(plot_widget, manager, scale, show_nodes, show_elements, draw_pushover, pattern_tag)` | Itera cargas y delega a los helpers; desactiva `setUpdatesEnabled` durante el renderizado |
| `_draw_nodal_load(plot_widget, node, load, scale, um, unit_str, color_override, is_pushover)` | Dibuja `ArrowItem` para Fx y Fy con etiqueta de valor |
| `_draw_element_load(plot_widget, ni, nj, load, scale, um, unit_str, color_override)` | Dibuja bloque de carga distribuida (wy/wx) con líneas + flechas `ScatterPlotItem` vectorizadas |

**Colores:**

| Modo | Tipo | Color |
|------|------|-------|
| Normal | Nodal (Fx/Fy) | Naranja `#FF5722` |
| Normal | Distribuida (wx/wy) | Morado `#9C27B0` |
| Pushover | Fx/Fy | Cian `#00BCD4` |

**Detalle `_draw_element_load`:** usa `pg.PlotCurveItem(connect='pairs')` para techo + palitos y un único `ScatterPlotItem` con símbolo `QPainterPath` rotado para todas las puntas de flecha.

**Relacionado:** [[ProjectManager]], [[Loads]], [[ScaleManager]], [[UnitManager]]

---

## DeformationRenderer → [[DeformationRenderer]]

Dibuja la forma deformada del modelo con interpolación cúbica de Hermite.

**Clase:** `DeformationRenderer`

**Atributos:**

| Atributo | Descripción |
|----------|-------------|
| `deformed_items` | Lista de ítems del plot para limpiar |
| `pen_deformed` | Línea discontinua cian `#00E5FF` |
| `node_scatter` | `ScatterPlotItem` hoverable con tooltips de desplazamiento |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `draw_deformed(plot_widget, manager, displacements, scale_factor)` | Dibuja curvas deformadas + scatter de nodos con tooltip Dx/Dy/Rz |
| `clear(plot_widget)` | Elimina todos los ítems y limpia el scatter |
| `_compute_beam_curve(ni, nj, di, dj, scale, num_points=20)` | Interpola la curva de barra usando funciones de forma de Hermite (cúbica transversal + lineal axial) |
| `_on_hover(item, points, ev)` | Actualiza tooltip del scatter al pasar el cursor sobre un nodo |

**Algoritmo `_compute_beam_curve`:**
- Transforma desplazamientos globales → locales (axial `u`, transversal `v`)
- Interpolación axial lineal; interpolación transversal cúbica (polinomios `h1..h4`)
- Transforma resultado de vuelta a coordenadas globales

**Relacionado:** [[ProjectManager]], [[ScaleManager]], [[UnitManager]]

---

## MassivePolygonsItem → [[ForceDiagramRenderer]]

Objeto gráfico de alto rendimiento que dibuja todos los polígonos de diagramas en una sola llamada `paint()`, sin depender del árbol de ítems Qt. Evita cancelaciones `WindingRule` entre formas opuestas.

**Clase:** `MassivePolygonsItem(pg.GraphicsObject)`

| Atributo | Descripción |
|----------|-------------|
| `polygons` | Lista de `QPolygonF` a dibujar |
| `my_pen` | `QPen` compartido para todos los polígonos |
| `my_brush` | `QBrush` compartido para todos los polígonos |
| `_bounds` | `QRectF` bounding box unificado |

| Método | Descripción |
|--------|-------------|
| `boundingRect()` | Retorna bounding box unificado |
| `paint(painter, ...)` | Dibuja todos los polígonos con un solo `setPen/setBrush` |

**Usado por:** `ForceDiagramRenderer.draw_diagrams()` (crea un único `MassivePolygonsItem` al final del bucle de elementos)

---

## ForceDiagramRenderer → [[ForceDiagramRenderer]]

Dibuja diagramas de fuerzas (Momento, Cortante, Axial).

**Clase:** `ForceDiagramRenderer`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `draw_diagrams(plot_widget, manager, element_forces, type)` | Itera elementos, acumula polígonos y crea un único `MassivePolygonsItem` |
| `_draw_element_diagram_detailed(plot_widget, ele, values, locs, scale, color, u_type, polygons_buffer)` | Construye polígono de un elemento y añade etiquetas de texto en extremos |
| `clear(plot_widget)` | Elimina todos los ítems del plot |

**Tipos (`type`):**

| Valor | Color | Escala usada | Unidad |
|-------|-------|-------------|--------|
| `'M'` | Rojo `#FF5252` | `moment` | `UnitType.MOMENT` |
| `'V'` | Verde `#4CAF50` | `shear` | `UnitType.FORCE` |
| `'P'` | Naranja `#FF9800` | `axial` | `UnitType.FORCE` |

**Estrategia de cortante:** usa solo los extremos del vector `localForce` (`v_i = [1]`, `v_j = [4]`) para trazar una línea recta exacta en lugar de interpolar puntos interiores.

**Relacionado:** [[ForceDiagramRenderer]], [[ProjectManager]], [[ScaleManager]]

---

## YieldRenderer → [[YieldRenderer]]

Dibuja estado de fluencia (rótulas) y cruces de San Andrés sobre la forma deformada.

**Clase:** `YieldRenderer`

**Atributos:**

| Atributo | Descripción |
|----------|-------------|
| `yield_scatter` | ScatterPlotItem con puntos de rótula (color por estado DL/SL/NC) |
| `_cross_items` | Lista de PlotDataItem con los segmentos de las cruces |

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `draw_yield_state(plot, manager, step_yield_data, step_displacements)` | Dibuja rótulas sobre deformada |
| `draw_frozen_floors(plot, frozen_floors, frozen_columns, step_displacements, scale, manager)` | Dibuja cruces de San Andrés por vano congelado |
| `clear(plot)` | Limpia rótulas |
| `clear_crosses(plot)` | Limpia cruces |

**Flujo de `frozen_columns`:**
```
pushover_solver
  └─► freeze_floor() retorna cross_pairs  [(ni, nj), ...]  — 6 seg/vano
        ├─► 2 diagonales (X)
        ├─► borde superior e inferior
        └─► borde izquierdo y derecho
  └─► consolidated["frozen_columns"][y_level] = cross_pairs
        └─► animation_toolbar → structure_interactor → YieldRenderer.draw_frozen_floors()
```

**Colores de rótulas:**

| Estado | Color |
|--------|-------|
| DL | Amarillo `(220,180,0)` |
| SL | Naranja `(230,100,0)` |
| NC | Rojo `(210,0,0)` |

**Relacionado:** [[ProjectManager]], [[ScaleManager]]

## Conexión con ScaleManager

Todos los renderizadores usan `ScaleManager.instance().get_scale(type)`:

| Tipo | Descripción |
|------|-------------|
| `deformation` | Factor de deformación |
| `moment` | Factor para diagrama M |
| `shear` | Factor para diagrama V |
| `axial` | Factor para diagrama P |
| `load` | Factor para flechas de carga |

## Relaciones

```
Visualizers
├── StructureInteractor ──► Los instancia
├── ScaleManager ──► Obtenienen factores de escala
├── ProjectManager ──► Leen modelo y resultados
└── AnimationToolbar ──► Actualizan en tiempo real
```

## Relacionado Con

- [[StructureInteractor]] - Viewport que usa renderizadores
- [[ScaleManager]] - Proporciona factores de escala
- [[ProjectManager]] - Fuente de datos