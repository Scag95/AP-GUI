# Context Transfer: AP-GUI Project State
## Role Configuration
You are a Python/PyQt6 architecture assistant acting as a technical instructor. The user is learning OOP concepts during implementation. Do NOT write code directly unless explicitly requested. Provide step-by-step guidance, explain concepts, and let the user implement the code.

## Project Specifications
- **Purpose**: GUI application for OpenSees structural analysis engine.
- **Stack**: Python 3.12, PyQt6, PyQtGraph.
- **Architecture**: Strict separation between `src/analysis/` (business logic) and `src/ui/` (presentation). Visualized in `ARCHITECTURE.md`.
- **Naming Convention**: 
  - Variables/code: English.
  - UI text/comments: Spanish.
  - All user-facing strings must be in Spanish.

## Implementation Timeline (History)
### Session 1 & 2 (Initial Setup)
- Created project structure (MVC adapted).
- Implemented `Node` and `Element` (basic).
- Created `ProjectManager` (Singleton).
- Built `MaterialDialog` and `SectionDialog` (with visualizer).

### Session 3 (2026-01-24) - Model Generation
- Implemented `FrameGenerator` (The Wizard) to create 2D frames automatically.
- Created `StructureInteractor` using `pyqtgraph` to visualize the model.
- Connected Wizard -> Manager -> Visualizer.

### Session 4 (2026-01-25) - Advanced Interaction (COMPLETED)
1. **Persistence (JSON)**:
   - Implemented `to_dict()`/`from_dict()` in all analysis classes (`Node`, `Material`, `Section`, `Element`).
   - Implemented `ProjectManager.save_project()` and `load_project()`.
   - Connected `FileMenu` to these methods using `QFileDialog`.

### Session 5 (2026-01-25) - Advanced Interaction (COMPLETED)
1. **Visual Feedback**:
   - Implemented `_on_node_clicked` and `_deselect_all` in `StructureInteractor`.
   - Selected nodes turn RED and show a text label with their ID.
   - Clicking on the background clears the selection.
   
2. **Properties Panel (DockWidget)**:
   - Created `PropertiesPanel` (QDockWidget) + `QStackedWidget` for modular forms.
   - Created `NodeForms` to view and edit Node coordinates (X, Y).
   - Implemented CLEAN architecture with signals: `NodeForm.dataChanged` -> `PropertiesPanel.dataChanged` -> `MainWindow.refresh_project`.
   - Editing a node in the panel instantly updates the visualization.

3. **Bugfixes**:
   - Fixed `AttributeError: NoneType has no attribute updateSpots` when refreshing viz with a selected node (added selection reset logic).

### Session 6 (2026-01-26) - Restraints & Density (COMPLETED)
1.  **Restricciones (Fixity)**:
    -   Backend: `Node.fixity` implementado (`[0,0,0]`).
    -   UI: `RestraintsDialog` (Gestor Avanzado: lista, rangos, selección rápida) creado y conectado al Menú Define.
    -   UI: Checkboxes básicos añadidos a `PropertiesPanel`.
2.  **Densidad y Masa**:
    -   Backend: `rho` añadido a `Material`, `Concrete01`, `Steel01`.
    -   UI: `MaterialForms` actualizados para input de densidad (SpinBox).
    -   Backend: `Section.get_mass_per_length()` implementado para cálculo automático de masa lineal.
3.  **Refactorización**:
    -   Eliminados métodos `__repr__` innecesarios.
    -   Corrección de errores en `to_dict`/`from_dict` de Elementos (get vs brackets).

### Session 7 (2026-01-27) - Load System Implementation (COMPLETED)
1.  **Backend de Cargas**:
    -   Implementado `src/analysis/loads.py` usando `ABC` (Abstract Base Classes) para robustez.
    -   Clases `NodalLoad` (Fx, Fy, Mz) y `ElementLoad` (Wx, Wy).
    -   Integración en `ProjectManager` (save/load JSON soportado).
2.  **UI de Asignación**:
    -   Creado `src/ui/menus/assign_menu.py`.
    -   `ElementLoadsDialog`: Selección múltiple (lista y texto rango "1-5,7") e input de cargas.
    -   `NodalLoadsDialog`: Similar, para fuerzas puntuales.
3.  **Visualización**:
    -   Actualizado `StructureInteractor` para dibujar flechas (`pg.ArrowItem`) de cargas nodales.
    -   Flechas verdes para X, naranjas para Y, con etiquetas de texto.

### Session 8 (2026-01-29) - Visualization & CLI (COMPLETED)
1.  **View Options (UX)**:
    -   Implementado sistema de escalado de cargas (`load_scale`) con atajos (`Ctrl++` / `Ctrl+-`).
    -   Visualización de IDs (Tags) de Nodos y Elementos.
2.  **Command Line Interface (CLI)**:
    -   Creado `CommandLineWidget` (estilo AutoCAD moderno, transparente).
    -   Creado `CommandProcessor` para interpretar comandos (`tag nodes on`, `clear`, etc.).
    -   Integración limpia en `MainWindow` como DockWidget inferior.
3.  **Visualización Cargas Distribuidas**:
    -   Implementado dibujo de `ElementLoad` en `StructureInteractor`.
    -   Estilo uniforme rectangular para `Wy` (Naranja) y `Wx` (Morado).
    -   Corrección de geometría vectorial para la dirección de las flechas.

### Session 9 (2026-01-31) - Unit System & Base Integration (COMPLETED)
1.  **Framework de Unidades**:
    -   Backend: `UnitManager` central para gestionar conversiones. Definida base SI pura (m, N, Pa, kg).
    -   UI: Created `UnitSpinBox` widget that handles `Visual Value <-> Base Value` automatically.
    -   Applied to: `MaterialForms` (User inputs MPa -> Stored as Pa) and `SectionForms` (User inputs mm -> Stored as m).
2.  **Section Preview Pro**:
    -   Updated `SectionPreview` to draw reinforcement bars at real scale (using `pxMode=False`).
    -   Implemented dynamic, self-scaling axes with arrow styles (using `pg.ArrowItem`).
3.  **Validation**:
    -   Verified OpenSees Translator receives correct base values (25000000 Pa, 0.3 m) regardless of UI settings.

### Session 10 (2026-02-01) - Refactoring & Advanced Viz (THE BIG ONE)
1.  **Unit System Integration (Complete)**:
    -   Extended `UnitSpinBox` to `NodalLoadsDialog` and `ElementLoadsDialog`.
    -   User can now input 100 kN, stored as 100,000.0 N correctly.
    -   Implemented "Fill on Select" for all dialogs (Material/Section/Load), drastically improving UX.
2.  **Visualization Architecture Refactor**:
    -   **Problem**: `StructureInteractor` was becoming a God Class.
    -   **Solution**: Implemented Renderer Pattern (`ModelRenderer`, `LoadRenderer`, `DeformationRenderer`, `ForceDiagramRenderer`).
    -   `StructureInteractor` now acts strictly as a Coordinator.
3.  **Hermite Interpolation**:
    -   Implemented cubic Hermite shape functions in `DeformationRenderer`.
    -   Users can now see the *true* curvature of beams.
4.  **UX Improvements**:
    -   Shortcuts implemented: `Ctrl +/-` (Load Scale), `PgUp/PgDown` (Deformation Scale).
    -   Verified analysis workflow: Build -> Load -> Analyze -> Visual Deform.

### Session 11 (2026-02-01) - Unit System & Force Diagrams (COMPLETED)
1.  **Unit System Selector & Integration**:
    -   Implemented global `UnitSelectorWidget` (ToolBar).
    -   Integrated `UnitManager` into `ForceDiagramRenderer` and `LoadRenderer`.
    -   Visualizations now respect user units (display kN, but calculate in N).
2.  **Force Diagrams (M, V, P)**:
    -   Implemented `ForceDiagramRenderer` fully.
    -   Supports Moment (Red/Blue), Shear (Green), and Axial (Orange) diagrams.
    -   Developed hybrid extraction logic in `opensees_translator`:
        -   Axial/Moment: via `section force` (more stable for P-M interaction).
        -   Shear: via `localForce` (element equilibrium).
3.  **OpenSees Troubleshooting**:
    -   Encountered numerical artifacts in Cantilever Free Tip (Non-zero forces).
    -   Analyzed `test.py` provided by user to understand correct `ForceBeamColumn` implementation (`-iter`, `-mass`) and Analysis Settings (`Newton` vs `Linear`).
    -   Decision: Stabilized gravity analysis (Linear) and prepared architecture for dedicated Pushover module.

### Session 12 (2026-02-02) - Professional Scale & Commands (COMPLETED)
1. **Centralized Scale Management**:
   - Implemented `ScaleManager` (Singleton) independent of UI.
   - Refactored all Renderers to use `get_scale(type)`.
   - Auto-calculation logic based on bounding box.
   
2. **Advanced Commands & UX**:
   - Enhanced `CommandProcessor`:
     - `show/hide` [loads/deformed/diagrams/nodes/elements].
     - `scale` [load/deformation/moment/shear/node] [value].
     - `regen`: Recalculate scales instantly.
   - Granular control: `show diagrams V` (only shear), `show loads N` (only nodes).

3. **Physics & Visualization Core**:
   - **Section Aggregator**: Implemented automatic `Aggregator` wrapping for `FiberSections` to add Shear Stiffness (`Vy`).
   - **Force Renderer**: 
     - Replaced lines with Filled Polygons (`QGraphicsPolygonItem`).
     - Implemented Lobatto 5-point integration for non-linear diagrams.
   - **Load Renderer**: Optimized performance (updates disabled during draw) and visual balance.

### Session 13 (2026-02-03) - Interaction & UX Polish (COMPLETED)
1. **CRUD & Grid**:
   - Implemented `update_material` and `update_section` to modify properties without duplication.
   - Added `add_base_beams` checkbox to Grid Dialog for generating base beams (z=0).
   - Calculated mass per length in FrameGenerator and passed element mass to OpenSees translator.

2. **Visualization UX**:
   - **Force Diagrams**: Added text labels for end values.
   - **Deformation**: Implemented `ScatterPlotItem` for nodes with interactive tooltips (showing Dx, Dy, Rz).
   - **Load Renderer**: Fixed scaling issue. Geometry is now invariant to unit changes (base units), while labels respect user units. Distributed load labels moved above the roof.

### Session 16 (2026-02-07) - Self Weight & Pushover Stabilization (COMPLETED)
1.  **Self Weight Generation**:
    -   Implemented `SelfWeightDialog` in Tools menu.
    -   Robust logic to project gravity loads onto local element axes (Horizontal, Vertical, Inclined).
    -   Integrated `UnitSpinBox` for Acceleration (`g`).
2.  **Pushover Stabilization (The Fix)**:
    -   **Problem**: Model instability with P-Delta + Distributed Loads + Large Steps.
    -   **Solution**: 
        -   Implemented `KrylovNewton` algorithm with `NormDispIncr` test in both Gravity and Pushover phases.
        -   Reduced step size (increased steps) for robust convergence.
        -   Verified correct `model_debug.py` generation.
    -   **Physics**: Confirmed "infinite strength" behavior due to `Steel01` (no rupture) and low gravity loads.

### Session 17 (2026-02-07) - Adaptive Sequential Pushover (COMPLETED)
1.  **Architecture Refactoring**:
    -   Refactored `OpenSeesTranslator` into `ModelBuilder`, `GravitySolver`, and `PushoverSolver`.
    -   Implemented Facade Pattern to coordinate solvers.
2.  **Adaptive Algorithm (Freeze & Forward)**:
    -   Implemented `run_adaptive_pushover` loop: Run -> Detect -> Freeze -> Re-run.
    -   **Detection**: Robust mechanism detection based on Stiffness Degradation (Tangent) and Drift %.
    -   **Freezing**: Dynamic insertion of Rigid Trusses to stabilize failed floors.
    -   **Continuity**: Maintained Gravity Base Shear and Load Modes across cycles to ensure correct curve plotting.
3.  **Advanced Visualization**:
    -   Updated `PushoverResultsDialog` to color-code analysis cycles (Cycle 1 vs Cycle 2 vs Cycle 3).
    -   Centralized Pushover Results in `ProjectManager` for persistence (View via Menu).

### Session 18 (2026-02-13) - Moment Curvature & Plotting Refinement
1. **Moment-Curvature Analysis**:
   - Refactored `MomentCurvatureDialog` to handle variable integration points and fiber sections robustly.
   - Fixed mapping of force/deformation components.
   - Dynamic integration point detection from Element properties.
2. **Pushover Improvements**:
   - Improved Floor Nomenclature in Results Dialog (e.g., "Piso 1 (Y=3.00m)").
   - Fixed `PushoverSolver` logic to read forces from the *last* integration point (Top) dynamically, ensuring stability regardless of discretization.
   - **Attempted Feature (Reverted)**: Step-by-step deformation animation. Reverted due to renderer data format mismatch (`IndexError`).

## Pending Tasks (Priority Order)
### 1. Deformation Animation (Video)
-   **Objective**: Visualize the structure's deformation step-by-step during Pushover via a Slider.
-   **Implementation**:
    -   Capture full node displacement history in `PushoverSolver`.
    -   Add Slider in `PushoverResultsDialog`.
    -   Update `StructureInteractor` to render arbitrary deformation states without re-scaling.

### 2. Advanced Failure Logic
-   **Refinement**: Tune detection parameters (Sensitivity, Drift Limits) on more complex models.
-   **Material Degradation**: Implement `MinMax` wrapper to `Steel01/Concrete01` to simulate true rupture (force drop).

## Technical Context for Next Session
-   **Current State**: Pushover and Moment-Curvature analysis are stable. Deformation video feature was reverted and needs clean re-implementation.
-   **Next Steps**: Focus on implementing the "Deformation Video" feature correctly (passing full node data including rotation if needed).
