---
name: CommandLineWidget
description: Widget de línea de comandos con historial y área de log para la consola del proyecto
type: reference
---

# CommandLineWidget

Widget que combina un campo de entrada con historial (`HistoryLineEdit`) y un área de log con colores. Envía comandos al `CommandProcessor`.

**Archivo:** `src/ui/widgets/command_line.py`

## Clases

### HistoryLineEdit(QLineEdit)

Campo de texto con historial navegable por flechas ↑/↓.

| Función | Descripción |
|--------|-------------|
| `keyPressEvent(event)` | Navega por el historial al pulsar ↑/↓ |
| `add_history(text)` | Añade un texto al historial; mantiene máximo 50 entradas |

### CommandLineWidget(QWidget)

Contenedor principal con entrada y log.

| Función | Descripción |
|--------|-------------|
| `_on_enter()` | Lee el texto, lo envía al `CommandProcessor` y limpia el campo |
| `log_message(message, color, bold)` | Añade una línea HTML coloreada al área de log |

## Relaciones

```
CommandLineWidget
├── HistoryLineEdit ──► campo de entrada con historial
├── CommandProcessor ──► process_command(text)
└── MainWindow ──► dock widget inferior
```

## Relacionado Con

- [[CommandProcessor]] - Procesador de comandos de texto
- [[MainWindow]] - Lo aloja como dock
- [[Widgets]] - Índice de widgets
