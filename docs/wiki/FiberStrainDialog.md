# FiberStrainDialog

Widget MDI anclable que visualiza la sección transversal de fibras coloreada por deformación unitaria (strain) para cada paso del análisis pushover.

**Clase:** `FiberStrainDialog(QWidget)`  
**Archivo:** `src/ui/dialogs/fiber_strain_dialog.py`

## Propósito

Permite inspeccionar la evolución de deformaciones en cada fibra de la sección a lo largo del pushover. Diferencia entre `FiberSection` (visualizable) y `AggregatorSection` (sin fibras → mensaje informativo).

## Clases internas

### `_PatchItem(pg.GraphicsObject)`

Renderizador personalizado de rectángulos de fibras con QPen cosmético (grosor fijo en píxeles). Evita los gaps entre fibras que producen los símbolos de `ScatterPlotItem`.

```python
def paint(self, p, *_):
    border = QPen(QColor(80, 80, 80))
    border.setCosmetic(True)
    border.setWidthF(0.5)
    for rect, col in zip(self._rects, self._colors):
        p.setBrush(QBrush(QColor(*col)))
        p.setPen(border)
        p.drawRect(rect)
```

## Funciones

| Función | Descripción | Retorna |
|--------|-------------|---------|
| `_rebuild_section()` | Reconstruye escena al cambiar selector de elemento/sección | None |
| `_build_shapes(sec)` | Loop `nIz × nIy` (orden OpenSees) → rectángulos + barras acero | None |
| `_compute_global_scale()` | Escala simétrica global `±amp = max(|vmin|, |vmax|)` sobre todos los pasos | None |
| `_setup_labels()` | Crea `pg.TextItem` por fibra para mostrar valor de strain actual | None |
| `_update_colors()` | Aplica `_fiber_color` a cada fibra y actualiza HTML de labels | None |
| `_fiber_color(strain, fiber_idx)` | EC8 color si corresponde, sino gradiente | tuple(R,G,B) |
| `_strain_color(strain, vmin, vmax)` | Interpolación lineal azul→blanco→rojo | tuple(R,G,B) |
| `connect_to_animation(anim_toolbar)` | Conecta `step_slider.valueChanged` del toolbar | None |
| `_on_main_step(value)` | Sincroniza slider local sin re-emit (blockSignals) | None |

## Controles de UI

| Control | Función |
|---------|---------|
| Combo elementos | Selección de ForceBeamColumn / ForceBeamColumnHinge |
| Combo puntos de integración | Selección de sección (IP 1..N) |
| Slider de paso | Navega pasos de `fiber_history` |
| `pg.PlotWidget` | Vista 2D de la sección con fibras, acero y labels |

## Criterios de Color EC8

| Material | Condición | Color |
|----------|-----------|-------|
| Steel01 | `ε ≥ Fy/E0` (fluencia) | Amarillo (DL) |
| Concrete01 | `ε ≥ 0.75 × εcu` | Naranja (SL) |
| Concrete01 | `ε ≥ 1.25 × εcu` | Rojo (NC) |
| Resto | — | Gradiente azul-blanco-rojo |

Escala del gradiente: global simétrica `vmin = -amp`, `vmax = +amp` calculada una sola vez sobre todos los pasos.

## Notas Técnicas

- `fiberData` de OpenSees devuelve `z=0` para todos los fibers en análisis 2D (z es fuera del plano). Las posiciones Y/Z se reconstruyen desde la definición de `FiberSection.patches` con el orden de loop correcto: **outer=nIz (columnas), inner=nIy (filas)**.
- `_mat_tags` se obtiene vía `manager._ls_fiber_mat_tags(sec)` para mantener coherencia con el detector de estados límite.
- La sincronización con `AnimationToolbar` usa `blockSignals(True)` para evitar retroalimentación.

## Relaciones

```
FiberStrainDialog
├── ProjectManager ──► fiber_geometry, fiber_history, _ls_fiber_mat_tags()
├── FiberSection ──► definición de patches y layers
├── AnimationToolbar ──► step_slider (sincronización bidireccional)
├── AnalyzeMenu ──► lo instancia vía _show_fiber_strains()
└── MainWindow ──► add_tool_window() (modo MDI)
```

## Relacionado Con

- [[ProjectManager]] - Almacena fiber_geometry y fiber_history
- [[FiberSection]] / [[Sections]] - Datos de sección usados para posiciones
- [[AnimationToolbar]] - Slider principal sincronizado
- [[AnalyzeMenu]] - Abre este widget
- [[Dialogs]] - Índice de diálogos
