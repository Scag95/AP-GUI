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

### Session 4 (2026-01-25) - Persistence & Interaction (COMPLETED)
1. **Persistence (JSON)**:
   - Implemented `to_dict()`/`from_dict()` in all analysis classes (`Node`, `Material`, `Section`, `Element`).
   - Implemented `ProjectManager.save_project()` and `load_project()`.
   - Connected `FileMenu` to these methods using `QFileDialog`.
   
2. **Architecture Refactor (Signals)**:
   - Modified `ProjectManager` to inherit from `QObject`.
   - Implemented `dataChanged` signal to notify UI of changes.
   - `StructureInteractor` now auto-refreshes when Manager emits signal.

3. **Interaction**:
   - Implemented `_on_node_clicked` in `StructureInteractor`.
   - Enabled `hoverable=True` and `pxMode=True` for nodes.
   - Added `data` field to `ScatterPlotItem` to store `Node` objects.
   - Implemented visual feedback: Node turns RED upon selection (console prints TAG).

4. **Bugfixes**:
   - Fixed indentation error in `frame_generator.py` that caused missing columns in base floor.
   - Fixed `dict object is not callable` error in `load_project`.

## Pending Tasks (Priority Order)
### 1. Advanced Interaction (Next Session Primary Goal)
- **Visual Feedback**: Ensure only ONE node is red at a time (currently logic exists but verify reset).
- **Property Panel**: 
  - Create a DockWidget or SidePanel in `MainWindow`.
  - Display properties (x, y, tag) of the selected node/element.
  - Allow editing selected item properties (e.g., move a node).

### 2. OpenSees Analysis Engine (The "Brain")
- Implement `run_analysis()` in `ProjectManager`.
- **Translator**: Create logic to translate the internal object model (`Node`, `Element`, `Section`, `Material`) into OpenSees commands (`openseespy` or `.tcl`).
- **Execution**: Run the analysis and capture output.

### 3. Result Visualization
- Once analysis runs, visualize the **Deformed Shape**.
- Plot **Pushover Curves** (Base Shear vs Roof Displacement).

## Technical Context for Next Session
- **Key Files**: 
  - `src/ui/widgets/structure_interactor.py`: Where selection logic lives.
  - `src/ui/main_window.py`: Where we likely need to add the Property Panel.
  - `src/analysis/manager.py`: The brain that will eventually call OpenSees.
- **New Resource**: `ARCHITECTURE.md` contains the updated Mermaid diagrams of the system.
- **User Status**: User is very hands-on. Loves "The Golden Rule" (don't write code for them). Prefers clear explanation of logic -> User writes code -> We debug together.
