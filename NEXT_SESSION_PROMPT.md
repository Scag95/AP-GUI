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
### Completed (Session 2026-01-21)
1. **Sections Module (Logic & UI)**:
   - `ProjectManager` updated to handle `Section` objects (add, delete, get_all).
   - `src/ui/widgets/section_forms.py`: Created reusable `SectionForm` widget for input data.
   - `src/ui/dialogs/section_dialog.py` fully functional:
     - **Add Section**: Calculates geometry coords for `RectPatch` and `LayerStraight` based on user input (b, h, cover, reinforced bars). Creates `FiberSection` objects.
     - **Delete Section**: Removes from manager and UI list.
     - **Load Sections**: Correctly repopulates list using stored object names.
   - `src/analysis/sections.py`: Fixed indentation of `get_opensees_commands`.

### Pending Tasks (Priority Order)
1. **Section Visualization (User's Goal for Next Session)**:
   - Create a visualization widget to draw the Cross-Section.
   - Requirements:
     - Draw the Concrete `RectPatch` (Rectangle).
     - Draw the Steel Bars from `LayerStraight` (Points/Circles).
   - Potential Library: `pyqtgraph` (preferred for speed/interaction) or `Matplotlib`.
   - Integration: Add this viewer inside `SectionDialog` or Main Window to preview creation.

2. **Persistence**:
   - Save/Load project state (Materials + Sections) to JSON.

3. **Analysis Integration**:
   - Start connecting logical objects to actual OpenSees Tcl script generation.

## Technical Context for Next Session
- **Files of Interest**: 
  - `src/ui/dialogs/section_dialog.py`: Will need to host the new graph widget.
  - `src/analysis/sections.py`: Source of geometry data (`yI, zI` etc.) to be plotted.
  - `src/ui/widgets/section_forms.py`: Input source reference.
- **Key Concepts to Teach**: 
  - **Custom Painting/Plotting**: How to translate our data models (Patches/Layers) into visual items (Rects/ScatterPlots).
  - **Observer Pattern (Optional)**: Updating the plot when form values change.

## User Status
- User has successfully coupled the UI inputs with the Domain Logic (Creation of objects).
- User is comfortable with `PyQt6` layouts and basic signals.
- Next challenge: Graphical representation of data structures.
