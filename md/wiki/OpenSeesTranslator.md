# OpenSeesTranslator

Fachada que orquesta la construcción del modelo y ejecución de análisis en OpenSees.

## Clase
`OpenSeesTranslator`

## Propósito
Punto único de entrada para todas las operaciones de análisis. Delega la lógica compleja a solvers especializados.

## Funciones

| Función | Descripción | Retorna | Depende De |
|---------|-------------|--------|-----------|
| `build_model()` | Construye el modelo OpenSees completo | None | ModelBuilder |
| `run_gravity_analysis()` | Ejecuta análisis de gravedad | bool (éxito) | GravitySolver |
| `get_analysis_results()` | Obtiene resultados de gravedad | dict | GravitySolver |
| `run_pushover_analysis()` | Ejecuta pushover monotónico | dict | PushoverSolver |
| `run_adaptive_pushover()` | Ejecuta pushover adaptativo con freeze | dict | PushoverSolver |
| `run_modal_analysis()` | Ejecuta análisis modal | list (períodos) | PushoverSolver |
| `dump_model_to_file()` | Vuelca modelo a archivo | None | OpenSeesPy |

## Relaciones

```
OpenSeesTranslator
├── ModelBuilder ──► OpenSeesPy
├── GravitySolver ──► Resultados ──► Manager.gravity_results
└── PushoverSolver ──► Resultados ──► Manager.pushover_results
```

## Uso

```python
translator = OpenSeesTranslator()
translator.build_model()
translator.run_gravity_analysis()
results = translator.get_analysis_results()
```

## Relacionado Con

- [[ModelBuilder]] - Construye el modelo
- [[GravitySolver]] - Análisis de gravedad
- [[PushoverSolver]] - Análisis pushover
- [[ProjectManager]] - Almacena resultados
- [[AnalyzeMenu]] - Llama a esta clase