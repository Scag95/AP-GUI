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

## 🔴🔴 Prioridad 6: Análisis No Lineal y Pushover (EN PROGRESO)
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
    - [ ] Animación de la deformada paso a paso.

## 🟣 Mejoras de Visualización y UX (Futuro Inmediato)
- [ ] **NodalLoadsDialog y ElementLoadsDialog**:
    - [x] CheckBox para filtrar lista: "Mostrar solo nodos/elementos con carga".
    - [x] CheckBox para mostrar/ocultar IDs en el visor (Show Tags) directamente desde el diálogo.
- [x] **View Options (Comandos de Visualización)**:
    - [x] Toggle Visibility: Mostrar u ocultar etiquetas (Tags) de Nodos y Elementos (Comando: `tag`).
    - [x] Load Scaling: Input para escalar visualmente el tamaño de las cargas (Atajos: `Ctrl++`/`Ctrl+-`).

## 🎓 Deuda Técnica / Mejoras
- [x] **Sistema de Unidades (Core & Materials/Sections)**:
    - [x] Backend: `UnitManager` (Singleton) y `UnitType` (Length, Force, Stress, Density).
    - [x] UI: `UnitSpinBox` para conversión automática (Visual <-> Base).
    - [x] Integración: `MaterialForm` (MPa -> Pa) y `SectionForm` (mm -> m).
    - [x] **Mejora Visual SectionPreview**: Barras a escala real y ejes dinámicos.
    - [x] Integración en Cargas (`NodalLoads`, `ElementLoads`) y Grids.
- [ ] Añadir validaciones en los inputs (que valores no sean negativos, etc.).
- [ ] Implementar edición de elementos existentes (Forms para Elementos).
- [x] **Refactorización de Visualización (Patrón Renderer)**:
    - [x] Crear `ModelRenderer`, `LoadRenderer`, `DeformationRenderer`, `ForceDiagramRenderer`.
    - [x] Limpiar `StructureInteractor` delegando pintado a renderizadores.
- [x] **Visualización Avanzada (Deformada)**:
    - [x] Implementar interpolación cúbica de Hermite para vigas curvas.
    - [x] Implementar escalado dinámico de deformada (`PgUp`/`PgDown`).
