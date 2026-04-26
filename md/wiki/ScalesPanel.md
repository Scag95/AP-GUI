---
name: ScalesPanel
description: Panel de control de escalas de visualización (cargas, deformada, diagramas de fuerzas)
type: reference
---

# ScalesPanel

`QWidget` con `QDoubleSpinBox` por cada tipo de escala. Sincronizado bidireccionalmente con `ScaleManager`.

**Clase:** `ScalesPanel(QWidget)`  
**Archivo:** `src/ui/widgets/scales_panel.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `_create_spinbox(scale_key, min, max, step, decimals)` | Crea un spinbox conectado a `_on_spinbox_changed` y lo registra en `self.spinboxes` |
| `_update_all_spinboxes()` | Actualiza todos los spinboxes desde los valores del manager (sin emitir señales) |
| `_on_external_multiplier_changed(scale_type, multiplier)` | Sincroniza el spinbox correspondiente cuando el manager cambia el multiplicador por teclado |
| `_on_spinbox_changed(scale_type, value)` | Inyecta el nuevo multiplicador al `ScaleManager` |

## Escalas disponibles

| Clave | Descripción | Rango |
|------|-------------|-------|
| `node_size` | Tamaño de nodos | 0.1–10 |
| `load` | Escala de cargas | 0.1–100 |
| `deformation` | Amplificación deformada | 0–1000 |
| `moment` | Diagrama Momento | 0.1–100 |
| `shear` | Diagrama Cortante | 0.1–100 |
| `axial` | Diagrama Axial | 0.1–100 |

## Relaciones

```
ScalesPanel
├── ScaleManager ──► get/set multiplicadores; señal multiplier_changed
└── MainWindow ──► aloja como dock lateral
```

## Relacionado Con

- [[ScaleManager]] - Fuente de verdad de escalas
- [[MainWindow]] - Panel dock en la UI
- [[Widgets]] - Índice de widgets
