---
name: CommandConsole
description: Widget de consola con campo de entrada y área de texto para log de comandos
type: reference
---

# CommandConsole

`QWidget` simple con un `QLineEdit` de entrada y un `QTextEdit` de log. Emite `commandEntered` al confirmar con Enter.

**Clase:** `CommandConsole(QWidget)`  
**Archivo:** `src/ui/widgets/command_console.py`

## Señales

| Señal | Descripción |
|------|-------------|
| `commandEntered(str)` | Emitida al pulsar Enter con el texto del campo |

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `history` | `list[str]` | Historial de comandos introducidos |
| `history_index` | `int` | Posición actual en el historial |

## Funciones

| Función | Descripción |
|--------|-------------|
| `init_ui()` | Construye el layout con `QLineEdit` + `QTextEdit` |

## Relaciones

```
CommandConsole
├── CommandProcessor ──► conectado a commandEntered
└── MainWindow ──► dock inferior
```

## Relacionado Con

- [[CommandLineWidget]] - Widget alternativo con más funcionalidad (historial, colores)
- [[CommandProcessor]] - Procesador de comandos
- [[Widgets]] - Índice de widgets
