---
name: PushoverDialog
description: Diálogo modal para configurar y lanzar el análisis pushover (monotónico o adaptativo)
type: reference
---

# PushoverDialog

Diálogo modal para configurar el análisis pushover y ejecutarlo a través de `OpenSeesTranslator`. Soporta modo monotónico normal y modo adaptativo secuencial (Freeze Forward).

**Clase:** `PushoverDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/pushover_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `populate_nodes()` | Rellena el combo de nodos de control ordenados por Y descendente |
| `_on_load_type_changed(text)` | Muestra/oculta el selector de patrón cuando se elige `"Patrón Definido"` |
| `run_pushover()` | Lee los parámetros del formulario y llama a `run_pushover_analysis()` o `run_adaptive_pushover()`; al terminar abre `PushoverResultsWidget` |

## Controles

| Control | Descripción |
|--------|-------------|
| `combo_node` | Nodo de control (ordenado por Y) |
| `spin_drift` | Desplazamiento máximo (`UnitSpinBox LENGTH`, default 30 cm) |
| `spin_steps` | Número de pasos (default 1000) |
| `combo_load_pattern_type` | Modal / Uniforme / Patrón Definido |
| `combo_defined_pattern` | Patrón con cargas nodales en X (visible solo con "Patrón Definido") |
| `chk_adaptive` | Activa análisis adaptativo Freeze Forward |
| `freeze_method_combo` | Método de congelamiento: Springs / Node Fix / Load Pattern / Cruces de San Andrés |
| `chk_custom_failure` | Habilita criterios de fallo personalizados |
| `spin_sensitivity` | Sensibilidad de caída (% rigidez inicial, default 3%) |
| `spin_max_drift` | Deriva máxima de piso (default 8%) |
| `chk_show_loads` | Visualizar distribución de cargas tras el análisis |
| `progress_bar` | Barra de progreso (visible durante el análisis) |
| `lbl_progress` | Label de estado: muestra ronda y paso actuales |

## Flujo de ejecución

```
run_pushover()
├── Activa progress_bar + lbl_progress, deshabilita btn_run
├── translator.run_pushover_analysis(progress_callback)    # Monotónico
│   └── label: "Ejecutando análisis... Paso N / Total"
├── translator.run_adaptive_pushover(progress_callback)    # Adaptativo
│   └── label: "Ronda R de N | Paso N / Total"
└── PushoverResultsWidget(results) ──► add_tool_window()
    └── self.accept()  ← cierre automático al terminar
```

En caso de error se restaura el botón y se ocultan los widgets de progreso.

## Relaciones

```
PushoverDialog
├── ProjectManager ──► get_all_patterns(), pushover_results
├── OpenSeesTranslator ──► ejecuta análisis
├── PushoverResultsWidget ──► muestra curva de capacidad
├── UnitSpinBox ──► spin_drift
└── AnalyzeMenu ──► lo abre
```

## Relacionado Con

- [[OpenSeesTranslator]] - Ejecuta el pushover
- [[PushoverResultsWidget]] - Widget de resultados
- [[AnalyzeMenu]] - Menú que lo abre
- [[ProjectManager]] - Almacena `pushover_results`
- [[Solvers]] - `PushoverSolver` y `LoadPushoverGenerator`
