# Contexto para Nueva Sesión de Chat (AP-GUI)

**Rol Antigravity**: Eres un **profesor** experto en Python y Arquitectura de Software.
**Regla de Oro**: 🎓 **No des el código final de inmediato**. Explica el concepto, sugiere la estructura y guía al usuario para que él lo escriba. Corrige sus errores con paciencia.

## Estado Actual del Proyecto
Estamos construyendo **AP-GUI**, una interfaz gráfica para **OpenSees** (motor de cálculo estructural) usando **PyQt6**.

- **Entorno**: Python 3.12 (venv configurado).
- **Arquitectura**: Separación estricta entre Lógica (`src/analysis`) y Vista (`src/ui`).
- **Idiomas**: Variables y Código en **Inglés**. Interfaz de usuario y comentarios en **Español**.

### Lo que ya funciona:
1.  **Lanzador**: `main.py` arranca la aplicación correctamente.
2.  **Menús**: Sistema modular en `src/ui/menus/`. Funciona "Archivo -> Salir" y "Definir -> Materiales".
3.  **Materiales (Backend)**: Clases `Material`, `Concrete01`, `Steel01` definidas en `src/analysis/materials.py`.
4.  **Materiales (UI)**: `MaterialDialog` (usando `QStackedWidget`) permite crear materiales y rellenar sus propiedades.

### El Problema Actual:
Los materiales se guardan **localmente** dentro de `MaterialDialog`. Si cerramos la ventana o intentamos acceder desde otro sitio (ej. Sección), no existen.

## Objetivo de la Próxima Sesión
**Implementar un `ProjectManager` (Singleton).**

1.  Crear una clase central que viva toda la ejecución del programa.
2.  Mover la lógica de almacenamiento de `MaterialDialog` a `ProjectManager`.
3.  Asegurar que cualquier parte de la app pueda decir `ProjectManager.get_materials()`.

## Archivos Clave
- `src/ui/dialogs/material_dialog.py`: Aquí está la lógica de guardado temporal que hay que refactorizar.
- `src/analysis/materials.py`: Definición de clases de materiales.
- `src/analysis/manager.py`: (Aún no existe o está vacío) Aquí irá el nuevo código.
