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