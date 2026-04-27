# Log - AP-GUI Wiki

Historial de cambios y sesiones de la wiki.

## Formato

Cada entrada sigue el formato:
```markdown
## [YYYY-MM-DD] tipo | Título
```

**Tipos:**
- `ingest` - Nuevo archivo documentado
- `query` - Consulta respondida
- `lint` - Verificación de salud
- `update` - Actualización de página existente
- `refactor` - Reestructuración de la wiki
- `migration` - Movimiento de archivos

### [2026-04-27] update | Fix bugs yield pipeline + optimización YieldRenderer

**Archivos de código modificados:**

- `src/ui/visualizers/yield_renderer.py` — Reescrito: 3 ScatterPlotItem con brush fijo, `_accumulate_limit_states`, `_flush_scatter` con numpy, `_node_map` cacheado, `_last_step` para scrubbing inverso.
- `src/analysis/manager.py` — `_ls_yield_aggregator`: devuelve lista (no dict) y solo si ratio ≥ 1.0. `_ls_yield_fiber`: ratio de hormigón usa `get_nc_strain()`/`get_sl_strain()` en vez de fallback 1.0.
- `src/ui/widgets/structure_interactor.py` — `draw_kinematic_yield_step` acepta `step_index`.
- `src/ui/widgets/animation_toolbar.py` — `_on_slider_changed` pasa `step_index=value`.

**Bugs corregidos:**
1. `_ls_yield_aggregator` devolvía `dict` → crash silencioso en modelos con rótulas (AggregatorSection).
2. `_ls_yield_aggregator` retornaba datos para ratio > 0 (antes de ceder), contaminando el acumulador.
3. Ratio de fibras Concrete01 siempre 1.0 (hardcoded); ahora usa umbral EC8 correcto.
4. Scrubbing inverso del slider no reseteaba `_max_limit_state` → colores erróneos al retroceder.

**Archivos wiki modificados:**
- `YieldRenderer.md` — Reescrita completamente con nueva arquitectura.
- `ProjectManager.md` — Actualizada descripción de `_ls_yield_fiber` y `_ls_yield_aggregator`.
- `StructureInteractor.md` — `draw_kinematic_yield_step` ahora documenta `step_index`.
- `AnimationToolbar.md` — `_on_slider_changed` documenta paso de `step_index`.

---

### [2026-04-27] update | Wiki: ResultsMenu separado, comandos actualizados

**Archivos wiki modificados:**

- `ResultsMenu.md` (nuevo) — Documentación completa del menú Resultados con acciones, funciones y relaciones.
- `CommandProcessor.md` — Actualizada tabla de alias show/hide: removido `structure`, añadidos `nodes` (oculta nodos físicos), `elements` (oculta elementos físicos), `nodetag`/`elementtag` (labels), `hinges`/`crosses` (indicadores de fluencia).
- `AnalyzeMenu.md` — Eliminadas acciones de resultados (diagramas, deformada, pushover, etc.) — ahora en ResultsMenu. Nota indicativa añadida.
- `MainWindow.md` — Añadido `results_menu` a atributos. Añadida sección "Handlers de Comandos CLI" con `set_nodes_visible`, `set_elements_visible`, `set_hinges_visible`, `set_crosses_visible`. Añadido enlace a ResultsMenu en relaciones.
- `Menus.md` — Añadida entrada completa de ResultsMenu entre AnalyzeMenu y ToolsMenu. Actualizada AnalyzeMenu con referencia a ResultsMenu.

**Verificación de código:** Fix de cargas al cargar JSON confirmado en `_on_data_changed` (`show_loads_nodes=False`, `show_loads_elements=False`) y `_just_loaded_from_json` flag en manager.

---

### [2026-04-26] feat | FiberStrainDialog: visualización de fibras por paso pushover + fix _ls_yield_fiber

**Archivos fuente modificados:**

- `manager.py` — Fix `_ls_yield_fiber`: reemplaza lectura de `floor_limit_states` (nivel piso) por `_ls_section_states[(ele_tag, sec_num)]` para que cada bisagra se coloree de forma independiente. Nuevos atributos `fiber_geometry` y `fiber_history`. Nuevo método `capture_fiber_step()`: consulta `fiberData` de OpenSees para todos los elementos FiberSection, guarda geometría en la primera llamada y strains por paso.
- `pushover_solver.py` — Llama `manager.capture_fiber_step()` tras cada paso, junto a `capture_limit_state_step`.
- `fiber_strain_dialog.py` (nuevo) — `FiberStrainDialog(QWidget)` anclable en MDI. Renderiza sección 2D con `_PatchItem(pg.GraphicsObject)` (rectángulos exactos, sin gaps). Posiciones calculadas desde definición de sección (loop outer=nIz, inner=nIy) porque `fiberData` devuelve z=0 en 2D. Escala global simétrica `±amp`. Labels de strain con `pg.TextItem`. Colores EC8 (DL/SL/NC) por tipo de material; fallback gradiente azul-blanco-rojo. Slider sincronizado con `AnimationToolbar.step_slider`.
- `analyze_menu.py` — Acción "Deformaciones de Fibras" en submenú "Ver Resultados". Abre `FiberStrainDialog` vía `add_tool_window` y llama `connect_to_animation(anim_toolbar)`.

**Páginas wiki actualizadas:** `ProjectManager`, `Solvers`, `AnalyzeMenu`, `Dialogs`, nueva `FiberStrainDialog`.

---

### [2026-04-26] update | Correcciones diagrama de cortante, barra de progreso pushover y monitor de fallos

**Archivos fuente modificados:**

- `gravity_solver.py` — Cortante interpolado linealmente desde `localForce`, normalizado por longitud L del elemento (`loc_rel = loc/L`). Antes usaba valor constante del extremo I para todos los puntos.
- `pushover_solver.py` — Misma corrección de normalización en `_get_all_element_forces()`. Añadido `progress_callback` a `run_pushover` y `run_adaptative_pushover`. El adaptativo reporta progreso por ronda `(step, total, round_idx, MAX_ROUND)` y para automáticamente cuando todos los pisos estructurales están congelados.
- `failure_detector.py` — Monitor reformateado: imprime una sola vez al detectar fallos nuevos (usa `reported_floors`). `_calculate_tangent_stiffness` usa últimos 2 puntos.
- `pushover_dialog.py` — Añadida `QProgressBar` + `QLabel` de estado. Botón deshabilitado durante análisis. Dialog se cierra automáticamente (`accept()`) al terminar con éxito.
- `opensees_translator.py` — `run_pushover_analysis` y `run_adaptive_pushover` aceptan y propagan `progress_callback`.

**Páginas wiki actualizadas:** `GravitySolver`, `PushoverSolver`, `FailureDetector`, `PushoverDialog`, `OpenSeesTranslator`.

---

### [2026-04-25] ingest | Creación de 39 páginas wiki individuales + links bidireccionales

**Objetivo:** Cada `[[WikiLink]]` referenciado en páginas de índice (Dialogs, Menus, Widgets, Solvers, Visualizers, Loads, Element, Sections) debe tener su propio archivo `.md`.

**Archivos creados (39):**

Diálogos: `MaterialDialog`, `SectionDialog`, `GeometryDialog`, `PatternDialog`, `NodalLoadsDialog`, `ElementLoadsDialog`, `RestraintsDialog`, `PushoverDialog`, `GridDialog`, `SelfWeightDialog`, `MomentCurvatureWidget`, `PushoverResultsWidget`

Menús: `FileMenu`, `DefineMenu`, `AssignMenu`, `AnalyzeMenu`, `ToolsMenu`

Widgets: `AnimationToolbar`, `CommandLineWidget`, `MaterialForms`, `SectionForms`, `SectionPreview`, `ScalesPanel`, `UnitSpinBox`, `PropertiesPanel`, `UnitSelectorWidget`, `CommandConsole`, `PropertiesForms`

Solvers: `GravitySolver`, `PushoverSolver`, `FailureDetector`, `LoadPushoverGenerator`, `PushoverConfigurator`

Loads: `NodalLoad`, `ElementLoad`, `LoadPattern`

Visualizers: `ModelRenderer`, `LoadRenderer`, `DeformationRenderer`, `ForceDiagramRenderer`, `YieldRenderer`

Elementos/Secciones: `ForceBeamColumn`, `ForceBeamColumnHinge`, `FiberSection`, `AggregatorSection`

**Bidireccionalidad:** Actualizado encabezado `## X → [[X]]` en: `Dialogs.md`, `Menus.md`, `Widgets.md`, `Solvers.md`, `Visualizers.md`, `Loads.md`, `Element.md`, `Sections.md`.

---

### [2026-04-25] update | Auditoría completa de archivos .py — cobertura 100%

**Método:** `find src/ -name "*.py"` (57 archivos) comparado con entradas wiki.

**Resultado:** Los 5 `__init__.py` están vacíos y no requieren entrada. Los 52 archivos con contenido **todos tienen entrada wiki**. No faltaba ningún archivo.

**Entradas enriquecidas (estaban presentes pero escasas):**
- `Visualizers.md` — `ModelRenderer`: añadidos atributos de estilos, símbolos de nodo por fixity, `highlight_node()`. `LoadRenderer`: añadidos `_draw_nodal_load()`, `_draw_element_load()`, detalle de vectorización con `PlotCurveItem(connect='pairs')`. `DeformationRenderer`: añadidos atributos, `_compute_beam_curve()`, `_on_hover()`, algoritmo de Hermite.
- `Widgets.md` — `AnimationToolbar`: controles detallados (`chk_sync`), descripción completa de `_on_slider_changed`. `UnitSelectorWidget`: corregida herencia (`QComboBox`), tabla completa de presets, detalle de bloqueo de señales.

---

### [2026-04-25] update | Auditoría completa de clases — cobertura 100%

**Método:** `grep -rn "^class "` en `src/` comparado con entradas wiki.

**Clase faltante encontrada:** `MassivePolygonsItem(pg.GraphicsObject)` en `force_diagram_renderer.py`

**Cambios:**
- `Visualizers.md` — Añadida sección `MassivePolygonsItem` (atributos, métodos, propósito). Mejorada `ForceDiagramRenderer`: firma completa de `draw_diagrams` y `_draw_element_diagram_detailed`, tabla de tipos con colores/escalas/unidades, estrategia de cortante documentada.

**Resultado:** 76 clases en `src/` (excl. Modelo), todas con entrada en la wiki.

---

### [2026-04-25] update | Revisión completa de wiki — todos los nodos vacios completados

**Archivos wiki modificados:** `Menus.md`, `Dialogs.md`, `Widgets.md`, `Arquitectura.md`, `ModelBuilder.md`, `Element.md`, `Sections.md`, `CommandProcessor.md`

**Cambios (segunda pasada):**

- `Menus.md` — `AssignMenu`: funciones + tabla de acciones. `ToolsMenu`: funciones + submenú Cargas. `DefineMenu`: tabla de acciones + `setup_actions()`. `FileMenu`: tabla de acciones + `setup_actions()` + acción Salir. `AnalyzeMenu`: funciones con descripciones detalladas e indicación de atajo F5.
- `Arquitectura.md` — Eliminado `steel_yield_detector.py` (ya no existe; reemplazado por `ProjectManager._ls_*`).
- `ModelBuilder.md` — Corregido retorno de `freeze_floor()`: `(ghost_nodes, cross_pairs)`.
- `Element.md` / `Sections.md` — Referencias a `SteelYieldDetector` actualizadas a `ProjectManager._ls_*()`.
- `CommandProcessor.md` — Firma completa de `process_command()` con estructura interna.

---

### [2026-04-25] update | Nodos vacíos de wiki completados

**Archivos wiki modificados:** `Dialogs.md`, `Widgets.md`

**Cambios:**

- `Dialogs.md` — `ElementLoadsDialog`: añadidas funciones (`populate_patterns`, `populate_elements`, `select_from_text`, `_parse_input`, `apply_loads`, `clear_loads`, `on_element_selected`, `toggle_tags`) y descripción de controles.
- `Widgets.md` — `MaterialForms`: documentadas las 5 clases (`ConcreteForm`, `SteelForm`, `ElasticForm`, `HystereticForm`, `HystereticSMForm`) con campos y unidades.
- `Widgets.md` — `PropertiesForms`: documentadas `NodeForms` y `ElementForm` con funciones y señales.
- `Widgets.md` — `SectionForm / AggregatorForm`: ampliado con detalle de `SectionForm.set_data` (detección geométrica de layers) y `AggregatorForm` completo (añadir/eliminar DOFs).
- `Widgets.md` — `SectionPreview`: añadida `_setup_ui()`, elementos gráficos y comportamiento `pxMode=False`.
- `Widgets.md` — `CommandLineWidget`: añadida clase `HistoryLineEdit` con `keyPressEvent` y `add_history`.
- `Widgets.md` — `CommandConsole`: añadidos atributos `history` e `history_index`.

---

### [2026-04-25] fix | Cruces de San Andrés en pushover adaptativo

**Archivos modificados:** `model_builder.py`, `pushover_solver.py`, `yield_renderer.py`, `structure_interactor.py`, `animation_toolbar.py`

**Cambios:**

- `model_builder.py` — `freeze_floor` método `"crosses"`: reescrito para usar conectividad real de columnas (`story_columns`) pasada por el solver. Cada vano genera 6 Truss en OpenSees (2 diagonales + 4 bordes) y retorna `(created_nodes, cross_pairs)` con los mismos 6 pares para el renderer.
- `pushover_solver.py` — Extrae `story_columns = [(bot_tag, top_tag), ...]` del manager antes de cada freeze y lo inyecta en `floor_state`. Desempaqueta el retorno del builder como `(ghosts, cross_pairs)`. La condición de parada por colapso de última planta se omite cuando `freeze_method == "crosses"`.
- `yield_renderer.py` — `draw_frozen_floors` simplificado: cada elemento de `cross_pairs` es un segmento directo (diagonal o borde); se dibuja una línea por par sin heurísticas de offset.
- `structure_interactor.py` / `animation_toolbar.py` — `frozen_columns` se propaga por todo el pipeline desde `pushover_results` hasta el renderer.

**Wiki actualizada:** `Solvers.md`, `Visualizers.md`

---

### [2026-04-25] refactor | Detección de estados límite unificada en ProjectManager

**Archivos modificados:** `manager.py`, `materials.py`, `pushover_solver.py`, `material_forms.py`, `steel_yield_detector.py` (eliminado), `code_limit_state_detector.py` (eliminado)

**Cambios:**

- `materials.py` — `get_yield_strain/sl/nc` de `Hysteretic` y `HystereticSM` aceptan `sign` (+1/-1/0). Con signo correcto compara contra el lado positivo o negativo de la curva M-φ. Sin signo (legacy) retorna el mínimo.
- `material_forms.py` — `HystereticSMForm` cambia spinboxes de esfuerzo de `UnitType.STRESS` a `UnitType.MOMENT` (kNm). Etiquetas actualizadas: Esfuerzo→Momento, Deformación→Curvatura.
- `manager.py` — Nueva sección de detección EC8: `reset_limit_states()`, `capture_limit_state_baseline()`, `capture_limit_state_step(roof_disp)`, `get_floor_limit_states()` + helpers privados `_ls_*`. Un único loop por paso reemplaza los dos detectores previos, garantizando sincronización entre rótulas en deformada y puntos en curva pushover.
- `pushover_solver.py` — Elimina instanciación de `SteelYieldDetector` y `CodeLimitStateDetector`. Delega al manager. `yield_history` ya no se propaga en el dict de resultados.
- `steel_yield_detector.py` / `code_limit_state_detector.py` — **Eliminados**.

**Wiki actualizada:** `Solvers.md`, `ProjectManager.md`, `Materials.md`

---

### [2026-04-21] migration | Reorganización de estructura wiki

**Resumen:**
Creación de estructura de 3 capas: raw/, wiki/, raíz.

**Estructura final:**
```
md/
├── raw/                    # Documentos fuente (vacío)
├── wiki/                   # 20 archivos wiki
├── index.md               # Portada con quick links
├── schema.md              # Convenciones
└── log.md                 # Historial
```

**Decisión:** El "raw" es el código en `src/`. No se reorganiza nada. La wiki se actualiza automáticamente cuando trabajamos en código.

---

## Entradas

### [2026-04-21] refactor | Reorganización de estructura wiki

**Cambios:**
- Creación de carpetas `raw/` y `wiki/`
- Movimiento de todos los archivos .md a `wiki/`
- Creación de `schema.md` con convenciones
- Creación de `log.md` para historial
- Creación de `index.md` en raíz

**Archivos movidos:**
- `Arquitectura.md`
- `index.md` (ahora en wiki/)
- `ProjectManager.md`
- `OpenSeesTranslator.md`
- `ModelBuilder.md`
- `Node.md`
- `Element.md`
- `Materials.md`
- `Sections.md`
- `Loads.md`
- `Solvers.md`
- `FrameGenerator.md`
- `CommandProcessor.md`
- `MainWindow.md`
- `StructureInteractor.md`
- `Dialogs.md`
- `Menus.md`
- `Widgets.md`
- `Visualizers.md`
- `UnitManager.md`
- `ScaleManager.md`

### [2026-04-21] ingest | Documentación inicial completa

**Resumen:**
Documentación inicial de todo el código fuente en `src/`.

**Archivos documentados:**
- `Arquitectura.md` - Vista general del sistema
- `ProjectManager.md` - Gestor central de datos
- `OpenSeesTranslator.md` - Fachada para análisis
- `ModelBuilder.md` - Constructor del modelo
- `Node.md` - Clase nodo
- `Element.md` - Elementos viga-columna
- `Materials.md` - Modelos de materiales
- `Sections.md` - Secciones de fibra
- `Loads.md` - Sistema de cargas
- `Solvers.md` - Solvers especializados
- `FrameGenerator.md` - Generador de marcos
- `CommandProcessor.md` - Procesador CLI
- `MainWindow.md` - Ventana principal
- `StructureInteractor.md` - Viewport
- `Dialogs.md` - Diálogos modales
- `Menus.md` - Sistema de menús
- `Widgets.md` - Widgets reutilizables
- `Visualizers.md` - Renderizadores
- `UnitManager.md` - Sistema de unidades
- `ScaleManager.md` - Factores de escala

### [2026-04-21] update | Relations en todos los archivos

**Resumen:**
Actualización de todos los archivos con tablas de relaciones completas y funciones.

**Cambios:**
- Añadida tabla de funciones con descripción y retorno
- Añadida sección de relaciones con diagrama
- Actualizado ProjectManager con cache pushover

### [2026-04-22] update | Completar documentación de Dialogs y Widgets

**Resumen:**
Documentación completa de clases que faltaban en la wiki.

**Archivos actualizados:**
- `Dialogs.md` - Completadas entradas de MomentCurvatureWidget, RestraintsDialog, SelfWeightDialog, PushoverResultsWidget, GridDialog
- `Widgets.md` - Añadidas entradas de CommandConsole, UnitSelectorWidget

**Clases documentadas:**
- `PushoverResultsWidget` - Curvas de capacidad pushover con estados límite
- `MomentCurvatureWidget` - Análisis M-φ desde archivos .out
- `RestraintsDialog` - Restricciones nodales UX/UY/RZ
- `SelfWeightDialog` - Peso propio basado en densidad
- `GridDialog` - Generador de mallas estructurales
- `CommandConsole` - Widget CLI
- `UnitSelectorWidget` - Selector de unidades con presets