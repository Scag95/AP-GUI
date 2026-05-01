# AP-GUI Wiki

Documentación del proyecto **AP-GUI** — Análisis Estructural 2D con GUI para OpenSees.

Stack: PyQt6 + OpenSeesPy + pyqtgraph

Para detalles técnicos → [[Arquitectura]]

---

## src/analysis/

| | |
|-|-|
| [[ProjectManager]] | Singleton central |
| [[OpenSeesTranslator]] | Fachada análisis |
| [[ModelBuilder]] | Construye modelo OpenSees |
| [[Solvers]] | GravitySolver, PushoverSolver... |
| [[Node]] | [[Element]] | [[Materials]] |
| [[Sections]] | [[Loads]] | [[FrameGenerator]] |

## src/ui/

| | |
|-|-|
| [[MainWindow]] | Ventana principal |
| [[StructureInteractor]] | Viewport (pyqtgraph) |
| [[Dialogs]] | Material, Section, Pushover... |
| [[Menus]] | File, Define, Assign, Analyze |
| [[Widgets]] | PropertiesPanel, ScalesPanel... |
| [[Visualizers]] | Model, Load, Deformation... |

## src/utils/

| | |
|-|-|
| [[UnitManager]] | Sistema de unidades |
| [[ScaleManager]] | Factores de escala |

---

[[schema]] · [[log]] | 20 archivos