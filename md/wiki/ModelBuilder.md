# ModelBuilder

Construye el modelo completo de OpenSees desde los datos del ProjectManager.

## Clase
`ModelBuilder`

## Propósito
Traduce los datos del proyecto (nodos, materiales, secciones, elementos, cargas) en comandos de OpenSeesPy. Genera un script de debug en `model_debug.py`.

## Funciones

| Función | Descripción | Privada |
|---------|-------------|--------|
| `build_model()` | Construye el modelo completo | No |
| `log_command()` | Ejecuta y loguea comando OpenSees | Sí |
| `freeze_floor()` | Congela un piso en pushover adaptativo | No |
| `_build_nodes()` | Crea nodos y restricciones | Sí |
| `_build_materials()` | Crea materiales | Sí |
| `_build_sections()` | Crea secciones | Sí |
| `_build_elements()` | Crea elementos | Sí |
| `_build_patterns()` | Crea patrones de carga | Sí |

## Flujo de build_model()

```
1. wipe + model basic -ndm 2 -ndf 3
2. _build_nodes() ──► node, mass, fix
3. _build_materials() ──► uniaxialMaterial, MinMax
4. _build_sections() ──► section Fiber, Aggregator
5. geomTransf PDelta 1
6. _build_elements() ──► beamIntegration, element
7. _build_patterns() ──► timeSeries, pattern, load, eleLoad
```

## freeze_floor()

Método para pushover adaptativo. Recibe estado deformado y aplica restricciones:
- `spring`: Nodo fantasma + elemento zeroLength
- `fix`: Pattern estático con sp
- `crosses`: Cruces de San Andrés (Truss)

Retorna: `(ghost_nodes: list[int], cross_pairs: list[tuple])` — nodos fantasmas creados y pares de conectividad para el renderer.

## Relaciones

```
ModelBuilder
├── ProjectManager ──► Lee datos
├── OpenSeesTranslator ──► Lo instancia
├── OpenSeesPy ──► Ejecuta comandos
└── PushoverSolver ──► Llama freeze_floor()
```

## Debug

Genera `model_debug.py` con todos los comandos para playback offline.

## Relacionado Con

- [[OpenSeesTranslator]] - Lo usa
- [[ProjectManager]] - Fuente de datos
- [[Node]] - Nodos
- [[Element]] - Elementos
- [[Materials]] - Materiales
- [[Sections]] - Secciones
- [[Loads]] - Cargas
- [[PushoverSolver]] - Llama freeze_floor()