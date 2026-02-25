# Lista de Tareas AP-GUI

## 🔴 Prioridad 1: Arquitectura de Datos (Centralización)
- [x] **Crear `src/analysis/manager.py`**:
    - [x] Definir clase `ProjectManager` (Patrón Singleton).
    - [x] Implementar listas para materiales y secciones.
    - [x] Métodos para añadir/borrar/obtener items.
    - [x] **Implementar listas para nodos y elementos**:
        - [x] Actualizar `ProjectManager` con diccionarios para `nodes` y `elements`.
        - [x] Crear herramienta de generación automática de pórticos (Grid Wizard).
    - [x] **Persistencia de Resultados**:
        - [x] Centralizar almacenamiento de `gravity_results` y `pushover_results` en `ProjectManager`.
        - [x] Permitir acceso a resultados desde menús sin re-ejecutar análisis.

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
    - [x] **Visualizar Cargas Distribuidas (`ElementLoad`)**:
    - [x] Implementar método de dibujo en `StructureInteractor` (rectángulos + flechas).
    - [x] Unificar estilo visual para Wy y Wx.
- [x] **Propiedades Avanzadas de Elementos**:
    - [x] **Backend**: Añadir `mass_density` a `ForceBeamColumn` (para `-mass`).
    - [x] **UI**: Permitir editar densidad de masa en `ElementForm` (Pendiente integración final).
    - [x] **Generación Automática**: Tool para generar cargas de peso propio (`SelfWeightDialog`) con proyección geométrica para elementos inclinados.

## 🔵 Prioridad 5: Motor de Cálculo y Resultados
- [x] **Generación de Modelo OpenSees (`src/analysis/opensees_translator.py`)**:
    - [x] Traducir Nodos (con sus Restricciones).
    - [x] Traducir Elementos (con sus Transformaciones).
    - [x] Traducir Materiales y Secciones (Fiber).
    - [x] Traducir Cargas a `ops.pattern` y `ops.eleLoad`.
- [x] **Ejecución y Resultados**:
    - [x] Método `run_analysis()` (Gravedad).
    - [x] Capturar resultados (Desplazamientos, Reaciones).
    - [x] **Visualización**:
        - [x] Deformada (Hermite Cúbico + Escala Dinámica + Tooltips Interactivos).
        - [x] **Diagramas de Esfuerzos**: (M, V, P) funcionando (`ForceDiagramRenderer`) con escala de unidades y etiquetas de valor.
        - [x] Force Diagrams with Fill & Scale (Lobatto Integration).
        - [x] Load Visualization Optimized (Arrow sizes, speed, Unit invariant).
        - [x] Centralized Scale Manager.
        - [x] Section Aggregator (M+P+V auto-setup).

## 🔴🔴 Prioridad 6: Análisis No Lineal y Pushover
- [x] **Interacción Avanzada**:
    - [x] **Sistema Visual de Nodos**: Mejorar representación/interacción de nodos (Símbolos por restricción).
    - [x] **Element Properties Form**: Ver y editar propiedades de elementos seleccionados.
- [x] **Módulo Pushover Fase 1 (Puntual)**:
    - [x] Traducir lógica de `test.py` a `opensees_translator.py` (`run_pushover`).
    - [x] Configurar análisis `DisplacementControl` con Gravedad previa.
    - [x] Extraer Cortantes de Piso (Story Shears) robustos (via Reacciones).
- [x] **Módulo Pushover Fase 2 (Modal)**:
    - [x] Implementar lógica de `eigen(1)` y patrón de carga proporcional al modo.
    - [x] **Debug Eigen**: Resolver error `ArpackSolver` (Posible falta de masa en modelo).
    - [x] **Validación de Masa**: Asegurar que `rho` viaja de Material -> Sección -> Elemento -> OpenSees.
    - [x] Extraer Desplazamientos Modales de cada piso y normalizar.
- [x] **Debugging de Elementos (Estabilidad)**:
    - [x] Resolver discrepancias de fuerza en extremos libres (Equilibrio estricto con `-iter` vs Configuración Análisis).
    - [x] Implementar sistema de logs para validar comandos Tcl (`model_debug.py` robusto).
    - [x] Estabilización de análisis (Test NormDispIncr, KrylovNewton, Pasos pequeños).
- [x] **Visualización Pushover**:
    - [x] Ventana de gráficos X-Y (Curva Pushover) con unidades correctas.
    - [x] Visualización de ciclos de análisis con colores diferenciados (`cycle_id`).
    - [x] Nomenclatura mejorada (Piso 1, Piso 2...) en gráficos.

## ☢️ Prioridad 7: Pushover Iterativo Secuencial (Freeze & Forward)
El objetivo es obtener la curva de capacidad completa de todos los pisos, evitando que el fallo de un piso blando detenga el análisis de los otros.
- [x] **Refactorización de Arquitectura**:
    - [x] Separar lógica en `ModelBuilder`, `GravitySolver`, `PushoverSolver`.
    - [x] Convertir `OpenSeesTranslator` en patrón Facade.
- [x] **Core Algorítmico (`PushoverSolver`)**:
    - [x] `detect_failed_floors(results)`: Implementado criterio híbrido Drift + Rigidez Tangente con parámetros ajustables.
    - [x] `freeze_floor(floor_y)`: Implementado en `ModelBuilder` mediante Truss rígidos dinámicos.
    - [x] `run_adaptive_pushover()`: Bucle principal (Run -> Detect -> Freeze -> Re-Run) implementado y debuggeado.
    - [x] **Continuidad de Cargas**: Solucionado el problema de reseteo de gráficas (Gravity Base Shear) y vector de cargas modal fijo (`fixed_load_vector`).
    - [x] **Dynamic Solver**: Lectura correcta de fuerzas usando el último punto de integración (Top).
- [x] **Gestión de Resultados**:
    - [x] Concatenar curvas de capacidad de las diferentes fases con ID de ciclo.
    - [x] Mostrar en `PushoverResultsDialog` las curvas compuestas finales coloreadas por fase.
- [x] **Cálculo de Masas y Topología (Session 20)**:
    - [x] Implementar caché de topología (`get_floor_data`) en `ProjectManager` para agrupar nodos/elementos por piso con invalidación (`mark_topology_dirty`).
    - [x] Implementar `get_floor_masses` en `ProjectManager` (100% vigas, 50% columnas superior/inferior, exclusión de bases fijas).
    - [x] Integrar matriz de masas concentradas en la lógica de `PushoverSolver` para asegurar correcta inercia sísmica ($F_i = M_i \cdot \phi_i$).

## 🧱 Prioridad 8: Análisis Sección (Moment-Curvature)
- [x] **Backend**:
    - [x] Implementar recorders para 'section force' y 'section deformation'.
    - [x] Extraer dinámicamente columnas de datos basadas en `integration_points` y detección automática de componentes.
- [x] **UI**:
    - [x] `MomentCurvatureDialog` con selección de Elemento y Puntos de Integración (Multi-Selección).
    - [x] Gráficos interactivos M-Phi con pyqtgraph, corrección de unidades y ejes dinámicos.
    - [x] Solución de escalas automáticas (Fix: `enableAutoSIPrefix(False)`).

## 🧹 Prioridad 9: Refactorización (Clean Architecture)
- [x] **Descomponer PushoverSolver (God Class)**:
    - [x] Extraer lógica del patrón de cargas y análisis modal (`LoadPushoverGenerator`).
    - [x] Extraer lógica de detección de fallos y mecanismos (`FailureDetector`).
    - [x] Extraer cálculos topológicos redundantes (Optimizando llamadas repetitivas al Manager por un caché `floor_meta` super rápido).
    - [x] Dejar a la clase el único propósito de orquestar el flujo OpenSees.

## 🟣 Prioridad 10: Visualización Cinemática (Video)
- [x] **Pushover Deformada Paso a Paso**:
    - [x] Capturar historial de desplazamientos de todos los nodos en cada paso (`PushoverSolver`). Para ello, pre-computaremos los diccionarios y leeremos `ops.nodeDisp` para `Dx, Dy, Rz`.
    - [x] Implementar Slider en `PushoverResultsDialog` manejando un rango desde el paso `0` al paso final, emitiendo una señal `step_visualization_requested`.
    - [x] Conectar la señal con `StructureInteractor` (`draw_kinematic_step`) para visualizar el snapshot. 
    - [x] Bloquear escalas automáticas/ScaleManager durante la visualización dinámica para no tener saltos de dibujo abruptos.

## 🧱 Prioridad 10: Materiales con Degradación (MinMax)
- [ ] **Backend**:
    - [ ] Envolver `Steel01` y `Concrete01` en `MinMax` Material para simular ruptura/aplastamiento real.
    - [ ] Esto permitirá detectar caídas de fuerza "naturales" en el Pushover.
- [ ] **UI**:
    - [ ] Añadir campo `Rupture Strain` en `MaterialDialog`.