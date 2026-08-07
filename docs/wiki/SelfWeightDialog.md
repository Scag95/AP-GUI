---
name: SelfWeightDialog
description: Diálogo modal para generar automáticamente cargas de peso propio sobre elementos
type: reference
---

# SelfWeightDialog

Diálogo modal que calcula y aplica cargas distribuidas de peso propio (`ElementLoad`) a los elementos del modelo, usando la densidad de masa de cada elemento y g = 9.81 m/s².

**Clase:** `SelfWeightDialog(QDialog)`  
**Archivo:** `src/ui/dialogs/self_weight_dialog.py`

## Funciones

| Función | Descripción |
|--------|-------------|
| `populate_patterns()` | Rellena el combo con los patrones de carga disponibles |
| `generate_loads()` | Valida el formulario, convierte g a unidades base y llama a `apply_self_weight()` |
| `apply_self_weight(g, only_beams, delete_existing)` | Itera sobre elementos, calcula `wy = ρ·g·(dx/L)` y `wx = ρ·g·(dy/L)`, crea `ElementLoad` en el patrón destino; retorna cantidad de cargas generadas |

## Lógica de cálculo

```
W = ρ · g
wy = -W · (dx / L)    # Componente vertical
wx = -W · (dy / L)    # Componente axial
```

Clasificación viga: `|dy|/|dx| < 0.1` (pendiente < 10%).

## Controles

| Control | Descripción |
|--------|-------------|
| `combo_pattern` | Patrón de carga destino |
| `check_beams_only` | Aplicar solo a vigas horizontales |
| `check_delete` | Eliminar cargas distribuidas existentes en el patrón antes de generar |

## Relaciones

```
SelfWeightDialog
├── ProjectManager ──► get_all_elements(), add_load(), delete_load()
├── ElementLoad ──► crea instancias con wx, wy calculados
├── LoadPattern ──► patrón destino
└── AssignMenu ──► lo abre
```

## Relacionado Con

- [[Loads]] - `ElementLoad` generadas
- [[LoadPattern]] - Patrón que recibe las cargas
- [[AssignMenu]] - Menú que lo abre
- [[ProjectManager]] - Acceso a elementos y patrones
