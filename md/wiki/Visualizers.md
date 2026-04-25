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

## ModelRenderer

Dibuja la estructura básica: nodos y elementos.

**Clase:** `ModelRenderer`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `attach()` | Añade items al plot |
| `clear()` | Limpia elementos |
| `draw_structure()` | Dibuja nodos, elementos, etiquetas |

**Atributos:**

| Atributo | Descripción |
|----------|-------------|
| `scatter_nodes` | ScatterPlotItem para nodos |
| `element_items` | Mapa de elementos |
| `labels` | Lista de etiquetas |

**Señales:** `sigClicked` en elementos para selección

**Relacionado:** [[ScaleManager]]

---

## LoadRenderer

Dibuja flechas de carga.

**Clase:** `LoadRenderer`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `clear()` | Limpia cargas |
| `draw_loads()` | Dibuja cargas con filtrado por patrón |

**Colores:**

| Tipo | Color |
|------|-------|
| Carga nodal | Naranja `#FF5722` |
| Carga distribuida | Morado `#9C27B0` |
| Carga pushover | Cian `#00BCD4` |

**Relacionado:** [[ProjectManager]], [[Loads]]

---

## DeformationRenderer

Dibuja la forma deformada del modelo.

**Clase:** `DeformationRenderer`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `draw_deformed()` | Dibuja deformación |
| `clear()` | Limpia visualización |

**Relacionado:** [[ProjectManager]], [[ScaleManager]]

---

## ForceDiagramRenderer

Dibuja diagramas de fuerzas (Momento, Cortante, Axial).

**Clase:** `ForceDiagramRenderer`

**Funciones:**

| Función | Descripción |
|--------|-------------|
| `draw_diagrams()` | Dibuja diagramas según tipo |
| `clear()` | Limpia diagramas |

**Tipos:** `moment`, `shear`, `axial`

**Relacionado:** [[ProjectManager]], [[ScaleManager]]

---

## YieldRenderer

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