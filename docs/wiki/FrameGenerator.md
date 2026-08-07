# FrameGenerator

Generador automático de marcos 2D regulares.

## Clase
`FrameGenerator`

## Propósito
Genera automáticamente nodos y elementos para marcos regulares.

## Funciones

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `generate_2d_frame()` | Genera marco completo | None |

## generate_2d_frame()

```python
generate_2d_frame(stories, bays, story_height, bay_width,
               beam_sec_tag, col_sec_tag, integration_points,
               add_base_beams=False, transf_tag=1)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `stories` | int | Número de pisos |
| `bays` | int | Número de vanos |
| `story_height` | float | Altura de cada piso |
| `bay_width` | float | Ancho de cada vano |
| `beam_sec_tag` | int | Tag de sección para vigas |
| `col_sec_tag` | int | Tag de sección para columnas |
| `integration_points` | int | Puntos de integración |
| `add_base_beams` | bool | Incluir vigas en base (planta 0) |
| `transf_tag` | int | Tag de transformación geométrica |

## Algoritmo

```
1. Generar matriz de nodos: (bays+1) × (stories+1)
   - Tag: get_next_node_tag()
   - Coordenadas: (i*bay_width, j*story_height)

2. Generar columnas:
   - Para cada (i, j) donde j < stories
   - Conecta nodo (i,j) con (i,j+1)
   - Asigna masa desde sección

3. Generar vigas:
   - start_floor = 0 if add_base_beams else 1
   - Para cada j ≥ start_floor, i < bays
   - Conecta nodo (i,j) con (i+1,j)
   - Asigna masa desde sección
```

## Ejemplo

```python
gen = FrameGenerator()
gen.generate_2d_frame(
    stories=3,           # 3 pisos
    bays=2,              # 2 vanos
    story_height=3.0,      # 3m entre pisos
    bay_width=6.0,       # 6m entre columnas
    beam_sec_tag=2,       # Sección de viga
    col_sec_tag=1,        # Sección de columna
    integration_points=5 # 5 puntos de Gauss-Lobatto
)
```

Resultado: 12 nodos, 9 columnas, 8 vigas

## Relaciones

```
FrameGenerator
├── GridDialog ──► UI que llama
├── ProjectManager ──► Almacena nodos y elementos
└── Node / Element ──► Crea las clases
```

## Relacionado Con

- [[ProjectManager]] - Almacena nodos y elementos
- [[Node]] - Clase de nodo
- [[Element]] - Clase de elemento
- [[GridDialog]] - UI para generar mallas