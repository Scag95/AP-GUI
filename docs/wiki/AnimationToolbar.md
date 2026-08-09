# AnimationToolbar

Directorio `src/ui/widgets/animation_toolbar.py` que contiene la barra de herramientas de animación del análisis Pushover.

## Descripción

**Clase:** `AnimationToolbar(QToolBar)`

Barra de herramientas interactiva que permite recorrer paso a paso los resultados del análisis no lineal Pushover mediante un control deslizante (`QSlider`), actualizando en tiempo real la deformada, el estado de fluencia (rótulas) y los diagramas en la interfaz gráfica.

## Componentes y Atributos

| Componente / Atributo | Tipo | Descripción |
|-----------------------|------|-------------|
| `step_label` | `QLabel` | Muestra el estado del paso de animación actual |
| `step_slider` | `QSlider` | Control deslizante horizontal para cambiar de paso |
| `chk_sync` | `QCheckBox` | Casilla para sincronizar el paso con el visualizador Momento-Curvatura |

## Métodos

| Método | Descripción |
|--------|-------------|
| `load_pushover_results()` | Habilita y configura el slider según el número de pasos de desplazamiento del análisis Pushover |
| `_on_slider_changed(value)` | Actualiza la etiqueta y emite la sincronización del paso hacia la ventana principal y los viewports |

## Relacionado

- [[Widgets]] - Contenedor de widgets de la interfaz
- [[MainWindow]] - Ventana principal que gestiona el toolbar
- [[StructureInteractor]] - Renderiza la deformada según el paso de animación
- [[PushoverSolver]] - Generador de los resultados cacheados para la animación
