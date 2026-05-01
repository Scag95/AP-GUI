# CommandProcessor

Procesador de comandos CLI integrado en la aplicación.

## Clase
`CommandProcessor`

## Propósito
Procesa comandos de texto ingresados en la consola y ejecuta acciones o retorna mensajes.

## Singleton
```python
CommandProcessor()  # No es singleton, se instancia en MainWindow
```

## Funciones

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `process_command(command_str: str)` | Divide en `verb + args`, selecciona rama de comando y retorna resultado | `tuple(msg: str, action: dict\|None)` |

**Firma interna:**
```python
parts = command_str.split()
verb  = parts[0].lower()   # ej. "scale", "show"
args  = parts[1:]           # ej. ["moment", "0.5"]
```

## Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `analyze` | Ejecuta análisis de gravedad | `analyze` |
| `clear` | Limpia consola | `clear` |
| `scale` | Ajusta multiplicadores de escala | `scale moment 0.5` |
| `show` | Muestra elementos | `show loads` |
| `hide` | Oculta elementos | `hide deformed` |
| `regen` | Regenera escalas automáticamente | `regen` |
| `units` | Cambia unidad de longitud | `units mm` |
| `check` | Vuelca modelo a archivo | `check` |
| `exit` | Cierra la aplicación | `exit` |

## Alias de scale

| Alias | Tipo Real |
|-------|----------|
| `nodes`, `node` | `node_size` |
| `deformed`, `def` | `deformation` |
| `moments`, `m` | `moment` |
| `shear`, `v` | `shear` |

## Alias de show/hide

| Objetivo | Sub-arg | Acción |
|---------|---------|--------|
| `loads`, `load` | `n`/`e` | Cargas nodales/elementales |
| `diagrams` | `M`/`V`/`P` | Diagramas de fuerzas |
| `deformed`, `deformation` | - | Forma deformada |
| `nodes` | - | Oculta/muestra nodos físicos |
| `elements` | - | Oculta/muestra elementos físicos |
| `nodetag` | - | Etiquetas de nodos |
| `elementtag` | - | Etiquetas de elementos |
| `hinges` | - | Articulaciones plásticas (yield) |
| `crosses` | - | Indicadores de fluencia en fibras |

## Arquitectura

```
CommandLineWidget
    ↓ (commandEntered signal)
MainWindow.execute_command()
    ↓
CommandProcessor.process_command()
    ↓
[acción] → MainWindow viz_widget methods
[mensaje] → CommandLineWidget.log_message()
```

## Retorno de process_command()

```python
return (msg, action)
# msg: string para mostrar en consola
# action: dict para ejecutar {"action": "set_diagram_type", "value": "M"}
```

## Relaciones

```
CommandProcessor
├── MainWindow ──► Lo instancia y llama
├── CommandLineWidget ──► Emite commandEntered
└── ScaleManager ──► Ajusta escalas
```

## Relacionado Con

- [[CommandLineWidget]] - Widget de entrada
- [[MainWindow]] - Contiene el procesador
- [[ScaleManager]] - Gestor de escalas