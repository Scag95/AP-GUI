# AP-GUI Agent Configuration

## Proyecto

Aplicación de análisis estructural 2D con GUI para OpenSees.

- **Stack:** PyQt6 + OpenSeesPy + pyqtgraph
- **Código:** `src/`
- **Main:** `main.py`
- **Wiki:** `md/wiki/`

## Objetivo Principal

Trabajar en el código y, al cerrar sesión, sincronizar la wiki.

## Wiki (`md/wiki/`)

Documentación del proyecto siguiendo el patrón **LLM Wiki**:
- Cuando modificas código en `src/`, actualizas la wiki correspondiente
- El "raw source" es el código en `src/` (no mover nada)
- La wiki vive en `md/wiki/` junto con `md/schema.md`, `md/index.md`, `md/log.md`

### Estructura

```
md/
├── wiki/
│   ├── Arquitectura.md     # Diagrama de relaciones
│   ├── ProjectManager.md   # Cada archivo de código
│   ├── Solvers.md
│   └── ... (uno por archivo/clase principal)
├── index.md                # Portada con quick links
├── schema.md               # Este archivo
└── log.md                 # Historial de cambios
```

### Convenciones

1. **Enlace raw → wiki:**
   ```
   src/analysis/manager.py  → wiki/ProjectManager.md
   src/analysis/solvers/*.py → wiki/Solvers.md (índice)
   src/ui/main_window.py   → wiki/MainWindow.md
   ```

2. **Estructura de página wiki:**
   - Título + descripción breve
   - Tabla de funciones/métodos
   - Tabla de atributos
   - Diagrama de relaciones con otros archivos
   - Enlaces `[[WikiLink]]` a archivos relacionados

3. **Workflow por defecto:**
   - Lees/modificas código en `src/`
   - **NO actualices la wiki durante el trabajo** — solo al cerrar sesión
   - Al cerrar sesión: actualiza todos los archivos wiki modificados + entrada en `md/log.md`

   **Tip:** Para saber qué se modificó, usa `git diff` o recuerda mentalmente.

### Alias Útiles

```bash
# Cuando digas "documenta X", lee md/schema.md primero
# Cuando digas "consulta la wiki", busca en md/wiki/
```

## Reglas de Comportamiento

1. **Siempre responde en español** (lenguaje del proyecto)
2. **Respuestas concisas** — 1-3 líneas máximo
3. **No generes código sin preguntar** — excepto si me lo pides explícitamente
4. **Usa los skills disponibles** cuando aplique
5. **Antes de editar código fuente**, lee el archivo completo

## Atajos de Teclado (referencia)

| Atajo | Acción |
|-------|--------|
| `Ctrl++` | Aumentar escala de cargas |
| `Ctrl+-` | Disminuir escala de cargas |
| `PgUp` | Aumentar escala de deformación |
| `PgDown` | Disminuir escala de deformación |

## Contacto

Para dudas sobre el proyecto, consulta `md/wiki/Arquitectura.md` primero.