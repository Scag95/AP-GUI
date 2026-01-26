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

## Pending Tasks (Priority Order)
### 1. Sistema de Cargas (Loads System) - NEXT TARGET
-   **Diseño Robusto**: Crear `src/analysis/loads.py` o definir estructura en `Element`.
    -   Definir estructura de datos para cargas (Uniform, Point).
-   **UI de Cargas**:
    -   Implementar `ElementLoadsDialog` (basado en el boceto aprobado del usuario).
    -   Inputs: `wx`, `wy` (distribuidas), y preparación para puntuales.
-   **Integración**:
    -   Visualizar cargas en el `StructureInteractor` (flechas/líneas sobre elementos).

### 2. OpenSees Analysis Engine (The "Brain")
-   **Traductor Final**: Completar `src/analysis/opensees_translator.py`.
    -   Integrar: Nodos + Fixity + Mass + Elements + Loads + Patterns.
-   **Ejecución**:
    -   Gravedad (Linear Series).
    -   Pushover (Displacement Control).
-   **Output**: Capturar respuestas (JSON).

### 3. Deuda Técnica
-   Implementar sistema de unidades.
-   Añadir botón de eliminar elementos.

## Technical Context for Next Session
-   **New UI Concept**: `LoadsDialog` (Similar to `RestraintsDialog` but for Elements).
-   **Key Files**:
    -   `src/ui/dialogs/restraints_dialog.py`: Reference implementation for the Loads dialog.
    -   `src/analysis/sections.py`: Contains mass calc logic.
    -   `src/analysis/element.py`: Updated with density/mass logic.
-   **User Status**: Wants a **robust** load system before running analysis.
