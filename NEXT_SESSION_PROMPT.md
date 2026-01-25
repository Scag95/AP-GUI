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

## Pending Tasks (Priority Order)
### 1. OpenSees Analysis Engine (The "Brain") - NEXT TARGET
- **Translator**: Create logic to translate the internal object model (`Node`, `Element`, `Section`, `Material`) into OpenSees commands.
   - Create `src/analysis/opensees_translator.py`?
- **Execution**: Run the analysis using `openseespy` or calling `opensees.exe`.
- **Output Parsing**: Capture the results (displacements, forces).

### 2. Result Visualization
- Once analysis runs, visualize the **Deformed Shape** (Mode Shapes).
- Plot **Pushover Curves** (Base Shear vs Roof Displacement).

### 3. More Interaction
- Implement `ElementForm` in `properties_forms.py` to edit Element properties.
- Add deletion (Delete key) for selected nodes/elements.

## Technical Context for Next Session
- **Key Files**: 
  - `src/ui/widgets/structure_interactor.py`: Where selection logic lives.
  - `src/ui/widgets/properties_panel.py`: Where editing logic lives.
  - `src/analysis/manager.py`: The brain that will eventually call OpenSees.
- **New Architecture components**:
  - `PropertiesPanel` communicates with `MainWindow` via signals.
  - `StructureInteractor` emits `nodeSelected(node)` and `selectionCleared()`.
- **User Status**: User is mastering PyQt signals/slots and modular UI design. Ready for the heavy backend logic (OpenSees).
