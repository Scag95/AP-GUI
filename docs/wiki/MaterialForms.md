---
name: MaterialForms
description: Formularios de parámetros para cada tipo de material uniaxial
type: reference
---

# MaterialForms

Conjunto de `QWidget` que exponen los parámetros de entrada de cada material. Usados por `MaterialDialog` en un `QStackedWidget`.

**Archivo:** `src/ui/widgets/material_forms.py`

## Clases

| Clase | Material OpenSees | Campos principales |
|------|------------------|-------------------|
| `ConcreteForm` | Concrete04 | fc, ec0, ecu, ft, Ets, beta |
| `SteelForm` | Steel01 | Fy, E0, b, a1-a4, sigInit |
| `ElasticForm` | Elastic | E |
| `HystereticForm` | Hysteretic | s1p/n, e1p/n, s2p/n, e2p/n, s3p/n, e3p/n, pinchX/Y, damage1/2, beta |
| `HystereticSMForm` | HystereticSM | Igual que Hysteretic + preview de curva |

## Interfaz común

Cada form implementa:

| Función | Descripción |
|--------|-------------|
| `set_data(material)` | Carga los parámetros de un objeto material en los campos |
| `get_data()` | Retorna dict con los parámetros para construir el material |
| `update_plot()` | (HystereticForm/HystereticSMForm) Actualiza preview `pg.PlotWidget` en tiempo real |

## Relaciones

```
MaterialForms
├── MaterialDialog ──► usa QStackedWidget con un form por tipo
├── Materials ──► ConcreteUniaxial, SteelUniaxial, etc.
└── UnitManager ──► conversiones internas
```

## Relacionado Con

- [[MaterialDialog]] - Contenedor que usa estos forms
- [[Materials]] - Clases de material que se crean/editan
- [[Widgets]] - Índice de widgets
