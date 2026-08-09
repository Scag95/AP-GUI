# RunTests

Lanzador unificado de la batería de pruebas automatizadas del proyecto.

**Archivo:** `run_tests.py`

## Propósito

Proporciona un punto de entrada programático para ejecutar toda la suite de pruebas del proyecto AP-GUI utilizando el motor `pytest`.

## Funciones

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `run_all_tests()` | Imprime banner informativo en consola y ejecuta `pytest.main(["tests/", "-v", "--tb=short"])` | int (código de salida) |

## Uso

```bash
python run_tests.py
# O directamente:
pytest
```

## Relacionado Con

- [[Arquitectura]] - Estructura general del proyecto y testing
- [[ProjectManager]] - Validador de componentes probados por los tests
