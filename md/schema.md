# Schema - AP-GUI Wiki

Este documento define las convenciones para mantener la wiki de documentación del proyecto AP-GUI.

## Estructura de Carpetas

```
md/
├── raw/                    # Documentos fuente originales (inmutables)
├── wiki/                   # Wiki generada por el LLM (el LLM escribe aquí)
├── index.md                # Portada con índice
├── schema.md               # Este archivo (convenciones)
└── log.md                 # Historial de cambios
```

## Convenciones de Página

### Frontmatter (Opcional)

Para páginas importantes, considerar añadir:

```markdown
---
title: Nombre del archivo
created: 2026-04-21
type: concept | entity | reference
tags: [analysis, ui, core]
---
```

### Estructura de Página

Cada página debe seguir este orden:

1. **Título** - `# Nombre`
2. **Descripción breve** - 1-2 oraciones
3. **Tabla de Contenido** - Solo para páginas complejas
4. **Sección: Clase** - Nombre de la clase principal
5. **Sección: Propósito** - Para qué existe
6. **Sección: Atributos** - Tabla de atributos
7. **Sección: Funciones/Métodos** - Tabla de funciones
8. **Sección: Relaciones** - Diagrama o lista de archivos relacionados
9. **Sección: Relacionado Con** - Enlaces wiki a archivos relacionados

### Tablas de Funciones

Usar este formato:

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `nombre_func()` | Qué hace | tipo |

### Enlaces Wiki

- Usar `[[nombre]]` para enlazar a otros archivos
- Usar `[[carpeta/archivo]]` si hay ambigüedad
- Verificar que los enlaces existan antes de crear

## Convenciones de Nombres

| Tipo | Convención | Ejemplo |
|-----|------------|---------|
| Clase Python | PascalCase | `ProjectManager` |
| Función/ Método | snake_case | `add_node()` |
| Variable/Atributo | snake_case | `pushover_results` |
| Archivo wiki | PascalCase | `ProjectManager.md` |
| Archivo raw | Nombre del fuente | `articulo_sobre_pushover.pdf` |

## Reglas de Contenido

### Lo que SÍ debe incluir

- Descripción clara del propósito
- Lista de funciones/métodos con descripción
- Tabla de atributos si aplica
- Relaciones con otros archivos
- Enlaces `[[wiki]]` a archivos relacionados

### Lo que NO debe incluir

- Comentarios de implementación (para eso está el código)
- Información redundante que ya está en otro archivo
- Capturas de pantalla o imágenes (guardar en raw/)
- Tentativas o ideas no implementadas

## Workflow de Ingest (Codigo Fuente)

El "raw source" es el código en `src/`. Cuando se modifica código:

1. Leer/modificar el archivo en `src/`
2. **Actualizar automáticamente** la página wiki correspondiente en `wiki/`
3. Añadir entrada a `log.md` con summary de cambios

**Regla:** Cada sesión de trabajo implica actualizar la wiki.

### Raw vs Wiki

| Raw (Fuente) | Wiki (Documentación) |
|-------------|----------------------|
| `src/analysis/manager.py` | `wiki/ProjectManager.md` |
| `src/analysis/solvers/*.py` | `wiki/Solvers.md` (índice) |
| `src/ui/main_window.py` | `wiki/MainWindow.md` |

La carpeta `raw/` no se usa — el código fuente ya está en `src/`.

## Workflow de Query

Cuando se consulta la wiki:

1. Leer `index.md` para encontrar páginas relevantes
2. Leer las páginas encontradas
3. Si la respuesta es valiosa, crear nueva página en wiki
4. Actualizar `log.md` con la consulta

## Workflow de Lint

Periódicamente verificar:

- [ ] Contradicciones entre páginas
- [ ] Páginas huérfanas (sin enlaces entrantes)
- [ ] Referencias faltantes
- [ ] Contenido desactualizado
- [ ] Páginas que podrían fusionarse

## Herramientas

- **Obsidian** - IDE para editar y navegar
- **Graph view** - Ver conexiones entre páginas
- **Dataview** - Consultas dinámicas sobre frontmatter
- **qmd** (opcional) - Motor de búsqueda local