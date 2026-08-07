---
name: LoadPattern
description: Patrón de carga contenedor de NodalLoad y ElementLoad con factor multiplicador
type: reference
---

# LoadPattern

Contenedor de cargas (nodales y de elemento) con un factor multiplicador. Análogo al `pattern Plain` de OpenSees.

**Clase:** `LoadPattern`  
**Archivo:** `src/analysis/loads.py`

## Atributos

| Atributo | Tipo | Descripción |
|---------|------|-------------|
| `tag` | `int` | Identificador único |
| `name` | `str` | Nombre descriptivo |
| `factor` | `float` | Multiplicador global (default 1.0) |
| `loads` | `list[Load]` | Lista de `NodalLoad` y `ElementLoad` |

## Métodos

| Método | Descripción |
|-------|-------------|
| `add_load(load_obj)` | Añade una carga a `loads` |
| `remove_load(load_tag)` | Elimina la carga con el tag dado |
| `to_dict()` | Serializa patrón y todas sus cargas |
| `from_dict(data)` | Reconstruye patrón con sus cargas desde dict |

## Relaciones

```
LoadPattern
├── NodalLoad ──► loads[]
├── ElementLoad ──► loads[]
├── ProjectManager ──► get_all_patterns(), add_pattern()
├── PatternDialog ──► CRUD de patrones
├── NodalLoadsDialog ──► destino de cargas nodales
├── ElementLoadsDialog ──► destino de cargas de elemento
└── OpenSeesTranslator ──► ops.pattern('Plain', tag, ...)
```

## Relacionado Con

- [[Loads]] - Sistema completo
- [[NodalLoad]] - Carga nodal contenida
- [[ElementLoad]] - Carga de elemento contenida
- [[PatternDialog]] - Diálogo de gestión
- [[ProjectManager]] - Almacén de patrones
