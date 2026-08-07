---
name: NodalLoad
description: Carga puntual aplicada a un nodo (Fx, Fy, Mz)
type: reference
---

# NodalLoad

Carga puntual con tres componentes en 2D. Hereda de `Load(ABC)`.

**Clase:** `NodalLoad(Load)`  
**Archivo:** `src/analysis/loads.py`

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `tag` | `int` | Identificador único |
| `node_tag` | `int` | Nodo destino |
| `fx` | `float` | Fuerza horizontal [unidad base] |
| `fy` | `float` | Fuerza vertical [unidad base] |
| `mz` | `float` | Momento [unidad base] |

## Métodos

| Método | Descripción |
|-------|-------------|
| `to_dict()` | Serializa a dict para JSON |
| `from_dict(data)` | Crea instancia desde dict |

## Relaciones

```
NodalLoad
├── Load ──► clase base ABC
├── LoadPattern ──► contenedor (loads[])
├── NodalLoadsDialog ──► crea instancias
└── OpenSeesTranslator ──► lo escribe como ops.load()
```

## Relacionado Con

- [[Loads]] - Sistema completo de cargas
- [[LoadPattern]] - Patrón contenedor
- [[NodalLoadsDialog]] - Diálogo que crea/edita estas cargas
