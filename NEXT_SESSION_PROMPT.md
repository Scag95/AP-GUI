# Context Transfer: AP-GUI Project State
## Role Configuration
You are a Python/PyQt6 architecture assistant acting as a technical instructor. The user is learning OOP concepts during implementation. Do NOT write code directly unless explicitly requested. Provide step-by-step guidance, explain concepts, and let the user implement the code.

## Project Specifications
- **Purpose**: GUI application for OpenSees structural analysis engine.
- **Stack**: Python 3.12, PyQt6.
- **Architecture**: Strict separation between `src/analysis/` (business logic) and `src/ui/` (presentation).
- **Naming Convention**: 
  - Variables/code: English.
  - UI text/comments: Spanish.
  - All user-facing strings must be in Spanish.

## Current Implementation Status
### Completed (Session 2026-01-22)
1. **Visualization Module**:
   - Implemented `src/ui/widgets/section_preview.py` using `pyqtgraph`.
   - Drawing Logic: Renders concrete rect (gray/lines) and steel bars (red dots).
   - Integration: Connected to `SectionDialog` for **Real-Time Preview** (updates on form change).
   - Style: Engineering style axes (Blue Y-axis, Green Z-axis) fixed to the center.

2. **Analysis Foundation**:
   - Created `src/analysis/node.py`: Basic `Node` class with OpenSees command generation.
   - Created `src/analysis/element.py`: `ForceBeamColumn` class connecting two nodes.

### Pending Tasks (Priority Order)
1. **Data Management**:
   - Update `ProjectManager` (`src/analysis/manager.py`) to store lists/dicts of `Node` and `Element` objects.
   - Implement add/delete/get methods for these new entities.

2. **Frame Generator (Wizard)**:
   - Create a simplified tool to generate 2D Frames automatically.
   - Inputs: Number of stories, number of bays, beam section, column section.
   - Logic: Auto-generate the grid of Nodes and connect them with Elements.

3. **Global Visualization**:
   - Visualize the generated structure (Lines and Points) in the `MainWindow`.

## Technical Context for Next Session
- **Files of Interest**: 
  - `src/analysis/manager.py`: Needs update for nodes/elements.
  - `src/analysis/node.py` & `src/analysis/element.py`: Already created, ready to use.
  - `TODO.md`: Contains the roadmap.
- **Key Strategy**: 
  - The user chose **Option 1 (Wizard)** for generating models initially. We will build a generator that populates the underlying Node/Element objects.
  - We use `ForceBeamColumn` elements with "Lobatto" integration.

## User Status
- User has successfully integrated real-time graphics with PyQt signals.
- User prefers a "Wizard" approach for model creation rather than manual drawing node-by-node.
- Codebase is clean and modular.
