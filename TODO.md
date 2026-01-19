# Lista de Tareas AP-GUI

## 🔴 Prioridad 1: Arquitectura de Datos (Centralización)
El objetivo es sacar los datos de las ventanas y guardarlos en un gestor central.
- [ ] **Crear `src/analysis/manager.py`**:
    - [ ] Definir clase `ProjectManager` (Patrón Singleton).
    - [ ] Implementar listas para materiales, secciones, nodos y elementos.
    - [ ] Métodos para añadir/borrar/obtener items.
- [ ] **Refactorizar `MaterialDialog`**:
    - [ ] Que al dar a "Añadir", llame a `ProjectManager.instance().add_material(...)` en lugar de guardarlo en `self.materials_data`.

## 🟡 Prioridad 2: Definición de Secciones
- [ ] **Backend (`src/analysis/sections.py`)**:
    - [ ] Definir clase base `Section`.
    - [ ] Implementar `RectangleSection` (b, h, material).
    - [ ] Implementar `FiberSection` (composición avanzada).
- [ ] **UI (`src/ui/dialogs/section_dialog.py`)**:
    - [ ] Crear diálogo similar a Materiales.
    - [ ] **Reto**: Incluir un `QComboBox` que lea los materiales disponibles del `ProjectManager`.

## 🟢 Prioridad 3: Geometría y Visualización
- [ ] **Dibujo en `MainWindow`**:
    - [ ] Integrar `pyqtgraph` en el widget central.
    - [ ] Dibujar nodos y líneas (elementos) en tiempo real.
- [ ] **Interacción Gráfica**:
    - [ ] Poder seleccionar nodos con el ratón (Raycasting o similar).

## 🔵 Prioridad 4: Motor de Cálculo
- [ ] **Generación de Modelo OpenSees**:
    - [ ] Método `run_analysis()` en el Manager.
    - [ ] Traducir objetos Python -> Comandos OpenSees (`ops.node`, `ops.element`, etc.).
- [ ] **Visualización de Resultados**:
    - [ ] Graficar curva de Histéresis/Pushover.
    - [ ] Mostrar deformada.

## 🎓 Deuda Técnica / Mejoras
- [ ] Corregir la lógica de borrado en `MaterialDialog` (actualmente solo borra de la lista visual).
- [ ] Añadir validaciones (que fpc no sea negativo, etc.).
