# Lista de Tareas AP-GUI

## 🔴 Prioridad 1: Arquitectura de Datos (Centralización)
El objetivo es sacar los datos de las ventanas y guardarlos en un gestor central.
- [x] **Crear `src/analysis/manager.py`**:
    - [x] Definir clase `ProjectManager` (Patrón Singleton).
    - [x] Implementar listas para materiales y secciones.
    - [x] Métodos para añadir/borrar/obtener items.
    - [ ] **Implementar listas para nodos y elementos (Próxima Sesión)**:
        - [ ] Actualizar `ProjectManager` con diccionarios para `nodes` y `elements`.
        - [ ] Crear herramienta de generación automática de pórticos (Wizard).
- [x] **Refactorizar `MaterialDialog`**:
    - [x] Que al dar a "Añadir", llame a `ProjectManager` en lugar de guardarlo localmente.

## 🟡 Prioridad 2: Definición de Secciones
- [x] **Backend (`src/analysis/sections.py`)**:
    - [x] Definir clase base `Section`.
    - [x] Implementar `FiberSection` (composición de parches y capas).
    - [x] Lógica de generación de scripts OpenSees (`get_opensees_commands`).
- [x] **UI (`src/ui/dialogs/section_dialog.py`)**:
    - [x] Crear formulario de entrada (`SectionForm`).
    - [x] Incluir `QComboBox` que lea los materiales del `ProjectManager`.
    - [x] **Lógica de Creación**: Calcular coordenadas `y, z` para parches y barras basado validando inputs (b, h, recubrimiento).

## 🟢 Prioridad 3: Geometría y Visualización
- [x] **Visualización de Sección (`SectionDialog`)**:
    - [x] Crear widget gráfico (PyQtGraph/Matplotlib) para previsualizar la sección transversal.
    - [x] Dibujar rectángulo de concreto y puntos de acero según coordenadas generadas.
- [ ] **Dibujo en `MainWindow`**:
    - [ ] Integrar `pyqtgraph` en el widget central.
    - [ ] Dibujar nodos y líneas (elementos) en tiempo real.
- [ ] **Interacción Gráfica**:
    - [ ] Poder seleccionar nodos con el ratón.

## 🔵 Prioridad 4: Motor de Cálculo y Persistencia
- [ ] **Persistencia**:
    - [ ] Guardar/Cargar proyecto completo (Materiales + Secciones) a archivo JSON.
- [ ] **Generación de Modelo OpenSees**:
    - [ ] Método `run_analysis()` en el Manager.
    - [ ] Traducir objetos Python -> Comandos OpenSees.
- [ ] **Visualización de Resultados**:
    - [ ] Graficar curva de Histéresis/Pushover.
    - [ ] Mostrar deformada.

## 🎓 Deuda Técnica / Mejoras
- [ ] Añadir validaciones en los inputs (que valores no sean negativos, etc.).
- [ ] Implementar edición de elementos existentes (no solo crear/borrar).
