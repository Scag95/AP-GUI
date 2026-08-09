# Prompt técnico — Implementación de tests de verificación para AP-GUI

## Contexto

AP-GUI es una aplicación de escritorio para análisis estructural 2D desarrollada en Python con PyQt6. Utiliza OpenSees (a través de openseespy) como motor de cálculo. La arquitectura sigue un patrón MVC adaptado con:

- `ProjectManager` (Singleton + QObject) como núcleo de datos.
- `OpenSeesTranslator` como fachada de análisis.
- `ModelBuilder`, `PushoverSolver`, `FailureDetector`, `PushoverConfigurator`, `LoadPushoverGenerator` como solvers.
- Visualizadores PyQt6 que responden a la señal `dataChanged`.
- `UnitSpinBox` (extensión de QDoubleSpinBox) para gestión de unidades.

El objetivo es implementar una batería de tests automatizados que verifiquen el funcionamiento correcto de cada componente.

## Stack de testing recomendado

- `pytest` como framework principal.
- `pytest-qt` (`pytestqt`) para testing de widgets PyQt6.
- `QtTest` (`PyQt6.QtTest`) para simulación de eventos y `QSignalSpy`.
- `unittest.mock` para mocking del `ProjectManager` donde sea necesario.
- Tests deben poder ejecutarse con: `pytest tests/ -v`

## Estructura de carpetas sugerida en el repositorio

```
AP-GUI/
├── src/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures compartidas
│   ├── test_validation.py       # Test 1 — Validación de entrada
│   ├── test_engine.py           # Test 2 — Motor de cálculo
│   ├── test_communication.py    # Test 3 — Comunicación entre módulos
│   ├── test_reference.py        # Test 4 — Modelos de referencia
│   └── test_error_handling.py   # Test 5 — Gestión de errores
```

---

## Test 1 — Validación de entrada de datos y conversión de unidades

**Fichero:** `tests/test_validation.py`

### 1.1 Rechazo de valores fuera de rango en QDoubleSpinBox

**Descripción:** Verificar que los controles nativos de PyQt6 impiden la introducción de valores inconsistentes.

**Pasos:**
1. Instanciar un diálogo de material (`MaterialDialog`) con un `QDoubleSpinBox` configurado para el módulo de elasticidad.
2. Intentar introducir los siguientes valores y verificar el comportamiento:
   - Valor negativo (-20000.0) → El control debe rechazarlo o forzar el mínimo configurado.
   - Valor cero (0.0) → El control debe rechazarlo si el mínimo es > 0.
   - Valor superior al máximo (1.0e15) → El control debe truncar al máximo permitido.
3. Verificar que el botón "Aceptar" del diálogo permanece deshabilitado mientras haya campos con valores inválidos.

**Criterio de éxito:** Ningún valor inválido llega al `ProjectManager`. El diálogo solo se cierra con valores dentro del rango permitido.

### 1.2 Conversión correcta de unidades en UnitSpinBox

**Descripción:** Verificar que `UnitSpinBox` transforma correctamente de unidades de usuario a unidades base.

**Pasos:**
1. Instanciar un `UnitSpinBox` configurado para el tipo `UnitType.FORCE`.
2. Establecer el sistema de unidades actual a kilonewtons (kN).
3. Introducir el valor 10.0 en el spinbox.
4. Leer el valor base mediante `get_value_base()`.
5. Verificar que el valor base es exactamente 10000.0 (newtons).
6. Cambiar el sistema de unidades a newtons (N) mediante `UnitManager`.
7. Verificar que el spinbox ahora muestra 10000.0 pero el valor base sigue siendo 10000.0.

**Criterio de éxito:** La conversión es exacta (sin errores de redondeo por encima de la tolerancia de doble precisión). El cambio de unidades no altera el valor base almacenado.

### 1.3 Campos obligatorios no pueden quedar vacíos

**Descripción:** Verificar que los campos obligativos bloquean la aceptación del formulario.

**Pasos:**
1. Abrir el diálogo de creación de material (`MaterialDialog`).
2. Dejar el campo "Nombre" vacío.
3. Completar el resto de campos con valores válidos.
4. Verificar que el botón "Aceptar" está deshabilitado.
5. Introducir un nombre válido.
6. Verificar que el botón "Aceptar" se habilita.

**Criterio de éxito:** El diálogo solo permite aceptar cuando todos los campos obligatorios están completos y válidos.

---

## Test 2 — Motor de cálculo y traducción al dominio de OpenSees

**Fichero:** `tests/test_engine.py`

### 2.1 Viga empotrada con carga puntual

**Descripción:** Resolver una viga empotrada y comparar con la solución analítica.

**Modelo:**
- Longitud: L = 5.0 m
- Sección rectangular: b = 0.3 m, h = 0.5 m
- Material: E = 30 GPa (concreto elástico lineal)
- Inercia: I = b·h³/12 = 0.003125 m⁴
- Carga puntual en extremo libre: P = 10000 N
- Solución analítica: δ = P·L³ / (3·E·I) = 10000 · 125 / (3 · 30e9 · 0.003125) = 0.004444... m

**Pasos:**
1. Crear 2 nodos: (0,0) empotrado, (5,0) libre.
2. Crear 1 elemento `ForceBeamColumn` con la sección y material definidos.
3. Asignar restricción de empotramiento en el nodo 1 (fixity: [1,1,1]).
4. Aplicar carga nodal en el nodo 2: Fy = -10000 N.
5. Ejecutar análisis de gravedad (estático lineal) a través de `OpenSeesTranslator`.
6. Extraer el desplazamiento vertical del nodo 2.

**Criterio de éxito:** El desplazamiento numérico coincide con el analítico con tolerancia relativa ≤ 1.0e-6.

### 2.2 Pórtico elástico con carga lateral

**Descripción:** Resolver un pórtico simple y comparar con matriz de rigidez manual.

**Modelo:**
- 2 columnas verticales: altura 3.0 m, sección cuadrada 0.4×0.4 m, E = 30 GPa.
- 1 viga horizontal: luz 6.0 m, sección igual.
- Nodos en base empotrados, carga lateral en nodo superior izquierdo: 5000 N.

**Pasos:**
1. Generar el pórtico mediante `FrameGenerator` o manualmente.
2. Asignar empotramientos en la base.
3. Aplicar carga lateral.
4. Ejecutar análisis estático lineal.
5. Extraer desplazamiento horizontal del nodo cargado.
6. Comparar con resultado de cálculo matricial manual (pre-calcular con script auxiliar de numpy).

**Criterio de éxito:** Desplazamiento coincidente con tolerancia relativa ≤ 1.0e-5.

### 2.3 Unicidad de tags en ModelBuilder

**Descripción:** Verificar que `ModelBuilder` no produce colisiones de identificadores.

**Pasos:**
1. Crear un modelo con 50 nodos, 100 elementos, 5 materiales, 10 secciones.
2. Ejecutar `ModelBuilder.build_model()`.
3. Capturar la salida de errores de OpenSees.

**Criterio de éxito:** No se producen errores de "tag already exists". El modelo se construye sin excepciones.

---

## Test 3 — Comunicación entre módulos y persistencia

**Fichero:** `tests/test_communication.py`

### 3.1 Emisión y recepción de dataChanged

**Descripción:** Verificar que la señal `dataChanged` se emite y los visualizadores responden.

**Pasos:**
1. Instanciar `ProjectManager` (o usar singleton existente).
2. Crear un `QSignalSpy` conectado a `ProjectManager.dataChanged`.
3. Invocar `ProjectManager.add_node(x=0, y=0)`.
4. Verificar que `spy.count()` es exactamente 1.
5. Invocar `ProjectManager.add_node(x=1, y=0)`.
6. Verificar que `spy.count()` es exactamente 2.
7. Crear un `StructureInteractor` de prueba conectado al manager.
8. Invocar `add_node()` nuevamente.
9. Verificar que el interactor actualizó su cuenta interna de nodos.

**Criterio de éxito:** La señal se emite exactamente una vez por operación de modificación. Los visualizadores actualizan su estado.

### 3.2 Persistencia JSON bidireccional

**Descripción:** Verificar que guardar y cargar conserva la integridad del modelo.

**Pasos:**
1. Crear un modelo completo:
   - 3 materiales (Concrete01, Steel01, Elastic)
   - 4 secciones (2 FiberSection, 2 AggregatorSection)
   - 12 nodos (pórtico 2×3)
   - 18 elementos (ForceBeamColumn)
   - 2 patrones de carga (gravitatorio, lateral)
2. Guardar a archivo JSON temporal mediante `ProjectManager.save_project()`.
3. Limpiar el manager (o instanciar uno nuevo).
4. Cargar el JSON mediante `ProjectManager.load_project()`.
5. Comparar conteos:
   - `len(get_all_nodes())` == 12
   - `len(get_all_elements())` == 18
   - `len(get_all_materials())` == 3
   - `len(get_all_sections())` == 4
   - `len(get_all_patterns())` == 2
6. Verificar que las propiedades de un material específico son idénticas (mismo nombre, mismos parámetros).

**Criterio de éxito:** Todos los conteos coinciden. Las propiedades individuales son idénticas post-carga.

---

## Test 4 — Procedimiento pushover adaptativo (end-to-end)

**Fichero:** `tests/test_reference.py`

### 4.1 Modelo 1-DOF elástico — curva lineal

**Descripción:** Verificar comportamiento lineal en régimen elástico.

**Modelo:**
- 2 nodos: (0,0) fijo, (1,0) libre.
- 1 elemento ` truss` elástico: A = 0.01 m², E = 200 GPa, L = 1.0 m.
- Rigidez axial: K = E·A/L = 2.0e9 N/m.

**Pasos:**
1. Construir modelo.
2. Configurar pushover estándar (no adaptativo) con control de desplazamiento.
3. Aplicar 10 incrementos de Δu = 0.001 m.
4. Extraer cortante basal V y desplazamiento u en cada paso.

**Criterio de éxito:** La relación V/u es constante e igual a K (2.0e9 N/m) en todos los pasos, con tolerancia ≤ 1.0e-6.

### 4.2 Detector de fallos con rigidez degradada

**Descripción:** Verificar que `FailureDetector` detecta agotamiento cuando la rigidez tangente cae.

**Pasos:**
1. Simular una historia de desplazamientos y cortantes de planta:
   - Pasos 1-10: comportamiento lineal (K_ini = 1000 kN/m)
   - Pasos 11-20: degradación controlada (K_tan decreciente)
   - Paso 20: K_tan = 0.5 kN/m (0.05% de K_ini)
2. Configurar `FailureDetector` con sensibilidad = 0.001.
3. Ejecutar `FailureDetector.analyze(results)`.

**Criterio de éxito:** El detector identifica el fallo en el paso donde K_tan/K_ini < 0.001. No reporta falsos positivos en pasos anteriores.

### 4.3 Inyección de cruces de San Andrés sin errores

**Descripción:** Verificar que la fijación de planta opera sin errores de dominio.

**Modelo:** Pórtico de 2 plantas, 1 vano, elementos elásticos.

**Pasos:**
1. Ejecutar pushover adaptativo hasta que el detector identifique la primera planta crítica.
2. Verificar que `ModelBuilder` inyecta 2 elementos truss diagonales en el vano de la planta agotada.
3. Verificar que los tags de los nuevos elementos no colisionan con existentes.
4. Continuar la siguiente ronda.

**Criterio de éxito:** La inyección no lanza excepciones. La siguiente ronda inicia sin errores de "tag already exists".

---

## Test 5 — Gestión de errores y situaciones límite

**Fichero:** `tests/test_error_handling.py`

### 5.1 Falta de convergencia con incremento excesivo

**Descripción:** Verificar la secuencia de fallbacks y la interrupción controlada.

**Modelo:** Pórtico con degradación súbita de rigidez (cambio brusco intencionado).

**Pasos:**
1. Configurar pushover con Δu = 0.05 m (excesivamente grande para el modelo).
2. Ejecutar análisis.
3. Capturar el log de estrategias activadas:
   - Verificar que se intenta KrylovNewton primero.
   - Verificar que se activa búsqueda lineal (factor 0.8).
   - Verificar que se intenta Broyden.
   - Verificar que se intenta Newton modificado.
   - Verificar que se intenta norma de energía.
   - Verificar que se activa sub-stepping (división en 10 sub-pasos).
4. Verificar que, al agotarse todas las estrategias, la ronda se interrumpe.
5. Verificar que el programa conserva los resultados hasta el último paso convergido.
6. Verificar que el mensaje de error indica: número de ronda, número de paso, tipo de error.

**Criterio de éxito:** Todas las estrategias se ejecutan en el orden previsto. El programa no se bloquea. El estado se conserva.

### 5.2 Mecanismo completo tras fijación de todas las plantas

**Descripción:** Verificar finalización ordenada cuando no quedan plantas por analizar.

**Modelo:** Pórtico de 1 planta, 1 vano.

**Pasos:**
1. Ejecutar pushover adaptativo.
2. Esperar que el detector identifique la única planta como crítica.
3. Verificar que el programa fija la planta.
4. Verificar que el programa detecta que no quedan plantas sin congelar.
5. Verificar que el análisis finaliza sin intentar una nueva ronda.

**Criterio de éxito:** El programa genera las curvas de capacidad y finaliza sin errores. No intenta iniciar una ronda imposible.

### 5.3 Modelo incompleto — detención antes de ejecución

**Descripción:** Verificar que un modelo inconsistente se detiene antes del análisis.

**Pasos:**
1. Crear un elemento cuyo nodo final no existe en el dominio (tag de nodo inexistente).
2. Intentar ejecutar `ModelBuilder.build_model()`.

**Criterio de éxito:** Se lanza una excepción o error descriptivo antes de invocar OpenSees. El mensaje identifica el elemento problemático y el nodo faltante.

---

## Instrucciones finales para la IA implementadora

1. Cada test debe ser independiente: usar fixtures de `conftest.py` para inicializar y limpiar el estado entre tests.
2. El `ProjectManager` es Singleton: asegurar que se limpia entre tests (método `clear()` o instancia nueva).
3. Los tests de PyQt6 requieren un `QApplication`: usar la fixture `qapp` de `pytest-qt`.
4. Los tests que invoquen OpenSees deben ejecutarse en un entorno donde `openseespy` esté instalado.
5. Priorizar tests deterministas: evitar dependencias de aleatoriedad o del sistema de archivos.
6. Documentar cada test con docstring que indique: propósito, entrada, criterio de éxito.
7. Ejecutar la batería completa con: `pytest tests/ -v --tb=short`
