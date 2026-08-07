# ScaleManager

Singleton + QObject que gestiona los factores de escala para renderizado visual.

## Clase
`ScaleManager`

## Propósito
Proporciona factores de escala combinados (base × multiplicador) a los renderizadores.

## Singleton
```python
ScaleManager.instance()
```

## Arquitectura de Escalas

El sistema usa dos componentes:
- **Base scales** (`_base_scales`): Factores geométricos calculados automáticamente
- **User multipliers** (`_user_multipliers`): Ajustes visuales del usuario (default 1.0)

La escala real para renderizadores es: `base * multiplier`

## Escalas Base

| Tipo | Valor Default | Descripción |
|------|---------------|-------------|
| `deformation` | 1.0 | Factor de escala de deformada |
| `moment` | 0.003 | Factor para diagramas de momento |
| `shear` | 0.003 | Factor para diagramas de cortante |
| `axial` | 0.003 | Factor para fuerzas axiales |
| `load` | 0.0003 | Factor para flechas de carga |
| `reaction` | 0.3 | Factor para reacciones |
| `node_size` | 10.0 | Tamaño visual de nodos |

## Funciones

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `instance()` | Obtiene singleton | ScaleManager |
| `set_user_multiplier()` | Ajusta multiplicador visual | None |
| `get_user_multiplier()` | Retorna multiplicador actual | float |
| `set_base_scale()` | Actualiza base (para auto-scale) | None |
| `get_scale()` | Retorna escala total (base × mult) | float |
| `autocalculate_scales()` | Calcula escalas según modelo | None |

## Señales

```python
scale_changed(type, value)      # Factor combinado real para renderizadores
multiplier_changed(type, value) # Factor relativo del usuario
```

## autocalculate_scales()

Calcula escalas sugeridas basándose en el tamaño del modelo:
```python
L_char = max(width, height)
base_diagram = L_char * 0.003  # 0.3% para diagramas
```

## Relaciones

```
ScaleManager
├── StructureInteractor ──► Conecta escala_changed
├── Visualizers ──► Obtenienen get_scale()
├── ScalesPanel ──► Ajusta multiplicadores
└── ProjectManager ──► Accede a singleton
```

## Relacionado Con

- [[UnitManager]] - Sistema de unidades
- [[ScalesPanel]] - Panel UI para ajustar escalas
- [[Visualizers]] - Renderizadores que usan estas escalas