# Arquitectura

AP-GUI es una aplicación de escritorio para análisis estructural 2D desarrollada en Python usando PyQt6. Actúa como interfaz gráfica para OpenSees (vía `openseespy`) para realizar análisis no lineales, particularmente análisis de pushover.

## Diagrama de Relaciones

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        UI Layer (PyQt6)                          │
├────────────────────────────────────────────────────────────────────┤
│ MainWindow                                                          │
│   ├─ Menus (FileMenu, DefineMenu, AssignMenu, AnalyzeMenu, ToolsMenu)    │
│   ├─ Dialogs ──► ProjectManager                                     │
│   ├─ Widgets ──► ProjectManager, ScaleManager, UnitManager            │
│   └─ Visualizers ──► ScaleManager, resultados del Manager              │
└────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                  ProjectManager (Singleton + QObject)                │
│  ├─ Almacena: materials, sections, nodes, elements, patterns         │
│  ├─ Resultados: gravity_results, pushover_results              │
│  ├─ Señal: dataChanged.emit()                                   │
│  └─ Cache: _floors_cache (topología de pisos)                      │
└────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                OpenSeesTranslator (Facade)                            │
│  ├─ ModelBuilder ──► OpenSeesPy                                 │
│  ├─ GravitySolver ──► Resultados ──► Manager.gravity_results    │
│  └─ PushoverSolver ──► Resultados ──► Manager.pushover_results  │
└────────────────────────────────────────────────────────────────┘
```

## Módulos

### src/analysis/ - Motor de Análisis

| Archivo | Clase Principal | Propósito | Relacionado Con |
|---------|--------------|---------|---------------|
| `manager.py` | ProjectManager | Gestor central de datos | Todo |
| `opensees_translator.py` | OpenSeesTranslator | Fachada para análisis | Manager, Solvers |
| `model_builder.py` | ModelBuilder | Construye modelo OpenSees | Manager |
| `node.py` | Node | Nodo estructural | Manager |
| `element.py` | Element, ForceBeamColumn, ForceBeamColumnHinge | Elementos | Manager, Sections |
| `materials.py` | Material, Concrete01, Steel01, Elastic, Hysteretic | Materiales | Manager |
| `sections.py` | Section, FiberSection, AggregatorSection | Secciones | Manager, Materials |
| `loads.py` | Load, NodalLoad, ElementLoad, LoadPattern | Sistema de cargas | Manager |
| `frame_generator.py` | FrameGenerator | Generador de marcos | Manager |
| `command_processor.py` | CommandProcessor | Comandos CLI | Manager |
| `solvers/gravity_solver.py` | GravitySolver | Análisis de gravedad | Manager |
| `solvers/pushover_solver.py` | PushoverSolver | Análisis pushover | Manager |
| `solvers/failure_detector.py` | FailureDetector | Detecta mecanismos de colapso | PushoverSolver |
| `solvers/load_generator.py` | LoadPushoverGenerator | Genera vectores de carga lateral | PushoverSolver |
| `solvers/pushover_configurator.py` | PushoverConfigurator | Configura análisis | PushoverSolver |

### src/ui/ - Interfaz Gráfica

| Archivo | Clase | Propósito | Relacionado Con |
|---------|-------|---------|-------------|
| `main_window.py` | MainWindow | Ventana principal | Manager, Menus, Dialogs |
| `dialogs/material_dialog.py` | MaterialDialog | Crear materiales | Manager |
| `dialogs/section_dialog.py` | SectionDialog | Crear secciones | Manager |
| `dialogs/geometry_dialog.py` | GeometryDialog | Nodos y elementos | Manager |
| `dialogs/pushover_dialog.py` | PushoverDialog | Configurar pushover | Translator, Manager |
| `dialogs/pattern_dialog.py` | PatternDialog | Gestionar patrones | Manager |
| `dialogs/nodal_loads_dialog.py` | NodalLoadsDialog | Asignar cargas nodales | Manager |
| `dialogs/element_loads_dialog.py` | ElementLoadsDialog | Cargas en elementos | Manager |
| `dialogs/pushover_result_dialog.py` | PushoverResultsWidget | Mostrar curva | Manager |
| `dialogs/moment_curvature_dialog.py` | MomentCurvatureWidget | Análisis M-φ | Manager |
| `dialogs/restraints_dialog.py` | RestraintsDialog | Restricciones | Manager |
| `dialogs/grid_dialog.py` | GridDialog | Generar mallas | FrameGenerator |
| `dialogs/self_weight_dialog.py` | SelfWeightDialog | Peso propio | Manager |
| `widgets/structure_interactor.py` | StructureInteractor | Viewport central | Manager, Visualizers |
| `widgets/properties_panel.py` | PropertiesPanel | Panel de propiedades | Manager |
| `widgets/animation_toolbar.py` | AnimationToolbar | Animación pushover | Manager |
| `widgets/scales_panel.py` | ScalesPanel | Ajustar escalas | ScaleManager |
| `widgets/unit_spinbox.py` | UnitSpinBox | Input con unidades | UnitManager |
| `widgets/section_preview.py` | SectionPreview | Preview de sección | Sections |
| `widgets/section_forms.py` | SectionForm, AggregatorForm | Formularios sección | Manager |
| `widgets/material_forms.py` | ConcreteForm, SteelForm, etc. | Formularios material | Manager |
| `widgets/properties_forms.py` | NodeForms, ElementForm | Formularios propiedades | Manager |
| `widgets/command_line.py` | CommandLineWidget | Consola CLI | CommandProcessor |
| `visualizers/model_renderer.py` | ModelRenderer | Dibuja modelo | ScaleManager |
| `visualizers/load_renderer.py` | LoadRenderer | Dibuja cargas | ScaleManager, Manager |
| `visualizers/deformation_renderer.py` | DeformationRenderer | Dibuja deformada | ScaleManager |
| `visualizers/force_diagram_renderer.py` | ForceDiagramRenderer | Dibuja M/V/P | ScaleManager |
| `visualizers/yield_renderer.py` | YieldRenderer | Dibuja fluencia | ScaleManager |
| `menus/file_menu.py` | FileMenu | Menú archivo | Manager |
| `menus/define_menu.py` | DefineMenu | Menú definir | Dialogs |
| `menus/assign_menu.py` | AssignMenu | Menú asignar | Dialogs |
| `menus/analyze_menu.py` | AnalyzeMenu | Menú analizar | Translator, Dialogs |
| `menus/tools_menu.py` | ToolsMenu | Menú herramientas | CommandProcessor |

### src/utils/ - Utilidades

| Archivo | Clase | Propósito | Relacionado Con |
|---------|-------|---------|---------------|
| `units.py` | UnitManager | Sistema de unidades | Todo (UI) |
| `scale_manager.py` | ScaleManager | Factores de escala | Visualizers |

## Patrones de Diseño

- **Facade**: OpenSeesTranslator
- **Singleton**: ProjectManager, UnitManager, ScaleManager
- **Observer**: ProjectManager.dataChanged
- **Builder**: ModelBuilder