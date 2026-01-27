# Lista de Tareas AP-GUI

## 🔴 Prioridad 1: Arquitectura de Datos (Centralización)
El objetivo es sacar los datos de las ventanas y guardarlos en un gestor central.
- [x] **Crear `src/analysis/manager.py`**:
    - [x] Definir clase `ProjectManager` (Patrón Singleton).
    - [x] Implementar listas para materiales y secciones.
    - [x] Métodos para añadir/borrar/obtener items.
    - [x] **Implementar listas para nodos y elementos**:
        - [x] Actualizar `ProjectManager` con diccionarios para `nodes` y `elements`.
        - [x] Crear herramienta de generación automática de pórticos (Grid Wizard).
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
- [x] **Dibujo en `MainWindow`**:
    - [x] Integrar `pyqtgraph` en el widget central.
    - [x] Dibujar nodos y líneas (elementos) en tiempo real.
- [x] **Interacción Gráfica**:
    - [x] Poder seleccionar nodos con el ratón (Feedback visual Rojo).
    - [x] Mostrar etiquetas de ID al seleccionar.
    - [x] Mostrar propiedades en Panel Lateral (DockWidget).
    - [x] **Edición**: Modificar coordenadas de nodos desde el panel y refrescar gráfico.

## 🟠 Prioridad 4: Inputs de Análisis (Pre-Cálculo)
- [x] **Condiciones de Contorno (Restricciones)**:
    - [x] **Backend**: Añadir atributo `fixity` a la clase `Node` (e.g., `[1, 1, 1]` para empotrado).
    - [x] **UI**: Crear herramienta/diálogo para seleccionar nodos y asignar restricciones (Fixed, Pinned, Roller).
- [x] **Cargas (Loads)**:
    - [x] **Backend**: Definir clases para Cargas (`NodalLoad`, `ElementLoad` con ABC).
    - [x] **UI**: Interfaz para asignar cargas puntuales (`NodalLoadsDialog`) y distribuidas (`ElementLoadsDialog`).
    - [x] **Visualización**: Flechas escalables en `StructureInteractor` para cargas nodales.
- [ ] **Propiedades Avanzadas de Elementos**:
    - [x] **Backend**: Añadir `mass_density` a `ForceBeamColumn` (para `-mass`).
    - [ ] **UI**: Permitir editar densidad de masa en `ElementForm` (Pendiente integración final).

## 🔵 Prioridad 5: Motor de Cálculo y Resultados
- [ ] **Generación de Modelo OpenSees (`src/analysis/opensees_translator.py`)**:
    - [ ] Traducir Nodos (con sus Restricciones).
    - [ ] Traducir Elementos (con sus Transformaciones).
    - [ ] Traducir Materiales y Secciones (Fiber).
    - [ ] Traducir Cargas a `ops.pattern` y `ops.eleLoad`.
- [ ] **Ejecución y Resultados**:
    - [ ] Método `run_analysis()` (Gravedad + Pushover).
    - [ ] Capturar resultados (Desplazamientos, Cortante Basal).
    - [ ] **Visualización**: Graficar curva de Histéresis/Pushover y Deformada.

## 🟣 Mejoras de Visualización y UX (Futuro Inmediato)
- [ ] **NodalLoadsDialog**: Filtrar lista para mostrar solo nodos que tengan cargas asignadas.
- [ ] **View Options (Comandos de Visualización)**:
    - [ ] Toggle Visibility: Mostrar u ocultar etiquetas (Tags) de Nodos y Elementos.
    - [ ] Load Scaling: Input para escalar visualmente el tamaño de las cargas.

## 🎓 Deuda Técnica / Mejoras
- [ ] **Sistema de Unidades**: Implementar convertidor y selector de unidades (N/mm, kN/m, etc.).
- [ ] Añadir validaciones en los inputs (que valores no sean negativos, etc.).
- [ ] Implementar edición de elementos existentes (Forms para Elementos).
