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

## Pending Tasks (Priority Order)
### 1. Mejoras de UX / Visualización (Refinamiento)
-   **View Options**: Toolbar/Menú para ocultar ID de nodos/elementos y escalar flechas de carga.
-   **Filtros UI**: Mejorar los diálogos para ver qué nodos ya tienen carga.
-   **Visualización de Element Loads**: Dibujar las cargas distribuidas sobre las vigas (actualmente solo se ven las nodales).

### 2. OpenSees Analysis Engine (The "Brain")
-   **Traductor Final**: Completar `src/analysis/opensees_translator.py`.
    -   Integrar: Nodos + Fixity + Elements + Loads + Patterns.
-   **Ejecución**: Gravedad y Pushover.
-   **Output**: Capturar respuestas JSON.

### 3. Deuda Técnica
-   Implementar sistema de unidades.
-   Añadir botón de eliminar elementos.

## Technical Context for Next Session
-   **Estado Actual**: El software ya permite modelar geometría completa y cargas. Falta pulir la visualización y conectar el cerebro (OpenSees).
-   **Archivos Clave**:
    -   `src/ui/widgets/structure_interactor.py`: Lógica de dibujo (flechas).
    -   `src/analysis/loads.py`: Definiciones de carga.
-   **Siguiente Paso**: Implementar controles de visualización (View Options) antes de pasar al motor de cálculo.
