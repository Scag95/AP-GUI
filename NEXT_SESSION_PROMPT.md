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

## Pending Tasks (Priority Order)
### 1. Pushover Analysis Module (High Priority)
-   **Objective**: Implement Non-linear Static Analysis based on `test.py` logic.
-   **Backend**: 
    -   Create `run_pushover_analysis` in translator.
    -   Implement `DisplacementControl` strategy.
    -   Configure proper Recorders (Drift, Base Shear).
-   **Frontend**: 
    -   Visualize Pushover Curve (Base Shear vs Roof Disp).
    -   Animation of plastic hinge formation (future).

### 2. Element Force Debugging
-   **Objective**: Achieve strict equilibrium in element forces (zero moment at free tip).
-   **Plan**: 
    -   Compare `opensees_script.tcl` generated by GUI vs `test.py`.
    -   Tune `ForceBeamColumn` integration and iteration settings.

## Technical Context for Next Session
-   **Estado Actual**: Gravity analysis works perfectly. Force diagrams are functional but show numerical noise in free ends due to model definition details.
-   **Recursos**: `test.py` is the Golden Reference for the Pushover implementation.
-   **Siguiente Paso**: Implementar el análisis Pushover replicando la lógica de `test.py`.
