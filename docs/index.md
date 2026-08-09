# AP-GUI Wiki Index

Documentación completa del proyecto **AP-GUI** — Análisis Estructural 2D con GUI para OpenSees.

**Stack Tecnológico:** Python 3.12+ · PyQt6 · OpenSeesPy · pyqtgraph

---

## 🏛️ Arquitectura y Gestión Central

| Artículo | Descripción |
|----------|-------------|
| [[Arquitectura]] | Visión general de la arquitectura del sistema |
| [[ProjectManager]] | Singleton central de estado del proyecto y modelo |
| [[ModelBuilder]] | Traductor y constructor del modelo numérico OpenSees |
| [[OpenSeesTranslator]] | Fachada de comunicación y ejecución con OpenSeesPy |

## ⚡ Análisis y Solvers

| Artículo | Descripción |
|----------|-------------|
| [[Solvers]] | Módulo general de resolvedores estructurales |
| [[GravitySolver]] | Solver de análisis estático gravitacional |
| [[PushoverSolver]] | Solver de análisis no lineal Pushover incremental |
| [[FailureDetector]] | Detector de colapso y falla de elementos/mecanismos |

## 📦 Entidades del Modelo Estructural

| Artículo | Descripción |
|----------|-------------|
| [[Node]] | Representación de nudos (coordenadas, grados de libertad, apoyos) |
| [[Element]] | Representación de elementos de barra / marco 2D |
| [[Materials]] | Definición de materiales elásticos y no lineales |
| [[Sections]] | Definición de secciones transversales y fibras |
| [[Loads]] | Estructura de cargas y patrones |
| [[LoadPattern]] | Patrones de carga (gravitacionales, laterales) |
| [[NodalLoad]] | Cargas puntuales asignadas a nodos |
| [[ElementLoad]] | Cargas distribuidas asignadas a elementos |
| [[FiberSection]] | Sección discretizada en fibras no lineales |
| [[AggregatorSection]] | Sección agregada con rigidez a corte/torsión |
| [[ForceBeamColumn]] | Elemento de marco basado en fuerzas con integración |
| [[ForceBeamColumnHinge]] | Elemento de barra con rótulas plásticas concentradas |

## 🛠️ Generadores de Geometría y Cargas

| Artículo | Descripción |
|----------|-------------|
| [[FrameGenerator]] | Generador de pórticos planos regulares y paramétricos |
| [[LoadPushoverGenerator]] | Generador de patrones de carga lateral Pushover |

## 🖥️ Interfaz Gráfica (UI Core)

| Artículo | Descripción |
|----------|-------------|
| [[MainWindow]] | Ventana principal MDI de la aplicación |
| [[StructureInteractor]] | Viewport gráfico interactivo 2D (`pyqtgraph`) |

## 📋 Menús de la Aplicación

| Artículo | Descripción |
|----------|-------------|
| [[Menus]] | Estructura general de la barra de menús |
| [[FileMenu]] | Menú Archivo (Nuevo, Abrir, Guardar, Exportar) |
| [[DefineMenu]] | Menú Definir (Materiales, Secciones, Patrones) |
| [[AssignMenu]] | Menú Asignar (Apoyos, Cargas, Restricciones) |
| [[AnalyzeMenu]] | Menú Analizar (Ejecutar Gravitacional, Pushover) |
| [[ResultsMenu]] | Menú Resultados (Deformada, Diagramas, Curva Pushover) |
| [[ToolsMenu]] | Menú Herramientas y utilidades |

## 🧩 Paneles, Widgets y Consola

| Artículo | Descripción |
|----------|-------------|
| [[Widgets]] | Módulo central de widgets reutilizables |
| [[AnimationToolbar]] | Barra de control de animación paso a paso Pushover |
| [[CommandConsole]] | Consola gráfica de salida de comandos y logs |
| [[CommandLineWidget]] | Campo de comandos CLI para interacción rápida |
| [[CommandProcessor]] | Procesador e intérprete de comandos CLI |
| [[PropertiesPanel]] | Panel lateral de inspección de propiedades |
| [[PropertiesForms]] | Formularios dinámicos del panel de propiedades |
| [[ScalesPanel]] | Panel de ajuste de factores de escala visuales |
| [[UnitSelectorWidget]] | Selector interactivo de unidades de trabajo |
| [[UnitSpinBox]] | SpinBox adaptativo con conversión automática de unidades |
| [[PushoverConfigurator]] | Widget de configuración de parámetros Pushover |
| [[PushoverResultsWidget]] | Widget de visualización de curva de capacidad y resultados |
| [[MomentCurvatureWidget]] | Widget de análisis y diagrama Momento-Curvatura |

## 💬 Diálogos de Configuración

| Artículo | Descripción |
|----------|-------------|
| [[Dialogs]] | Resumen de diálogos modales de la UI |
| [[GeometryDialog]] | Diálogo de parámetros geométricos |
| [[GridDialog]] | Diálogo de configuración de la rejilla del viewport |
| [[MaterialDialog]] | Diálogo de creación y edición de materiales |
| [[SectionDialog]] | Diálogo de asignación y definición de secciones |
| [[RestraintsDialog]] | Diálogo de asignación de condiciones de apoyo / fixity |
| [[PatternDialog]] | Diálogo de gestión de patrones de carga |
| [[NodalLoadsDialog]] | Diálogo de asignación de cargas nodales |
| [[ElementLoadsDialog]] | Diálogo de asignación de cargas distribuidas |
| [[SelfWeightDialog]] | Diálogo de activación e inclusión de peso propio |
| [[PushoverDialog]] | Diálogo de ejecución y control del análisis Pushover |
| [[FiberStrainDialog]] | Diálogo de inspección de deformaciones en fibras |

## 🎨 Formularios e Inspectores de Secciones

| Artículo | Descripción |
|----------|-------------|
| [[MaterialForms]] | Formularios de edición gráfica de materiales |
| [[SectionForms]] | Formularios de definición de perfiles y secciones |
| [[SectionPreview]] | Componente de vista previa 2D de sección transversal |

## 🎨 Renderizadores Gráficos (Visualizers)

| Artículo | Descripción |
|----------|-------------|
| [[Visualizers]] | Módulo de renderizadores gráficos del viewport |
| [[ModelRenderer]] | Renderizador de nodos, elementos y apoyos |
| [[LoadRenderer]] | Renderizador de vectores y bloques de carga |
| [[DeformationRenderer]] | Renderizador de forma deformada con curvas de Hermite |
| [[ForceDiagramRenderer]] | Renderizador de diagramas de momento, cortante y axial |
| [[YieldRenderer]] | Renderizador de rótulas plásticas y estado de fluencia |

## 📏 Unidades y Escalas (`src/utils/`)

| Artículo | Descripción |
|----------|-------------|
| [[UnitManager]] | Gestor global y conversor del sistema de unidades |
| [[ScaleManager]] | Gestor de factores de escala de deformación y diagramas |

---

## 📑 Documentación Adicional

- [Esquema de datos JSON](schema.md)
- [Registro de cambios y desarrollo](log.md)
- [Documento de Arquitectura Principal](ARCHITECTURE.md)

*Total de artículos en la Wiki:* **67 páginas**