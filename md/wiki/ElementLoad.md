---
name: ElementLoad
description: Carga distribuida uniforme aplicada a un elemento (wx, wy en coordenadas locales)
type: reference
---

# ElementLoad

Carga distribuida uniforme con componentes en el sistema de coordenadas local del elemento. Hereda de `Load(ABC)`.

**Clase:** `ElementLoad(Load)`  
**Archivo:** `src/analysis/loads.py`

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `tag` | `int` | Identificador único |
| `element_tag` | `int` | Elemento destino |
| `wx` | `float` | Carga axial distribuida [unidad base] |
| `wy` | `float` | Carga transversal distribuida [unidad base] |

## Métodos

| Método | Descripción |
|-------|-------------|
| `to_dict()` | Serializa a dict para JSON |
| `from_dict(data)` | Crea instancia desde dict |

## Relaciones

```
ElementLoad
├── Load ──► clase base ABC
├── LoadPattern ──► contenedor (loads[])
├── ElementLoadsDialog ──► crea instancias
├── SelfWeightDialog ──► genera automáticamente
└── OpenSeesTranslator ──► escribe como ops.eleLoad()
```

## Relacionado Con

- [[Loads]] - Sistema completo de cargas
- [[LoadPattern]] - Patrón contenedor
- [[ElementLoadsDialog]] - Diálogo que crea/edita estas cargas
- [[SelfWeightDialog]] - Generador automático de peso propio
