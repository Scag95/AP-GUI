"""
Script de diagnóstico: verifica si eleResponse puede leer fiberData
a través de un AggregatorSection usando distintas variantes de llamada.

Ejecutar desde la raíz del proyecto:
    python diagnostico_fibras.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.model_builder import ModelBuilder
from src.analysis.solvers.gravity_solver import GravitySolver
from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge

# ─── 1. Cargar proyecto ───────────────────────────────────────────────────────
ARCHIVO_PROYECTO = "Archivo de prueba.json"

manager = ProjectManager.instance()
ok = manager.load_project(ARCHIVO_PROYECTO)
if not ok:
    print(f"[ERROR] No se pudo cargar '{ARCHIVO_PROYECTO}'")
    sys.exit(1)
print(f"[OK] Proyecto cargado: {ARCHIVO_PROYECTO}")

# ─── 2. Construir modelo y correr gravedad ────────────────────────────────────
builder = ModelBuilder()
builder.build_model()

gravity = GravitySolver(builder)
ok = gravity.run()
if not ok:
    print("[ERROR] Falló el análisis de gravedad")
    sys.exit(1)

# ─── 3. Un paso de pushover mínimo para tener deformaciones ──────────────────
#  Aplicamos un desplazamiento pequeño en el nodo de control superior.
all_nodes = manager.get_all_nodes()
top_node  = max(all_nodes, key=lambda n: n.y)   # nodo con mayor coordenada Y

ops.timeSeries('Linear', 99)
ops.pattern('Plain', 99, 99)
ops.load(top_node.tag, 1.0, 0.0, 0.0)

ops.system('UmfPack')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('DisplacementControl', top_node.tag, 1, 5e-3)
ops.algorithm('Newton')
ops.analysis('Static')
ops.analyze(20)   # 20 pasos × 5mm = 100mm → provoca fluencia en acero
print("[OK] 20 pasos de análisis ejecutados")

# ─── 4. Seleccionar el primer ForceBeamColumnHinge disponible ─────────────────
ele_objetivo = None
for ele in manager.get_all_elements():
    if isinstance(ele, (ForceBeamColumn, ForceBeamColumnHinge)):
        ele_objetivo = ele
        break

if ele_objetivo is None:
    print("[ERROR] No se encontró ningún ForceBeamColumn en el modelo")
    sys.exit(1)

tag = ele_objetivo.tag
n_sec = ele_objetivo.integration_points
print(f"\n[INFO] Elemento elegido: tag={tag}, tipo={type(ele_objetivo).__name__}, secciones={n_sec}")

# ─── 5. Prueba directa de fiberData (FiberSection pura) ──────────────────────
separador = "─" * 60
print(f"\n{separador}")
print("  PRUEBA fiberData DIRECTO (sin AggregatorSection)")
print(separador)

for sec_num in [1, 2, 3]:
    datos = ops.eleResponse(tag, 'section', sec_num, 'fiberData')
    n_fibras = len(datos) // 5 if datos else 0
    print(f"\n  sec {sec_num} → {len(datos)} valores ({n_fibras} fibras)")
    for f in range(min(n_fibras, 4)):          # mostrar máx 4 fibras
        y, z, area, stress, strain = datos[f*5:(f+1)*5]
        print(f"    fibra {f}: y={y:.4f}  area={area:.4e}  stress={stress:.2e}  strain={strain:.2e}")

    deform = ops.eleResponse(tag, 'section', sec_num, 'deformation')
    print(f"  deformation → eps_axial={deform[0]:.2e}  kappa={deform[1]:.2e}")

# ─── 6. Verificar capture_step() con Bernoulli ────────────────────────────────
from src.analysis.solvers.steel_yield_detector import SteelYieldDetector

detector   = SteelYieldDetector()
step_data  = detector.capture_step()
separador  = "─" * 60
print(f"\n{separador}")

print(f"\n{separador}")
print(f"  RESULTADO capture_step()  —  {len(step_data)} elementos con fluencia")
print(separador)

for ele_tag, secs in list(step_data.items())[:5]:   # mostrar máx 5 elementos
    print(f"\n  Elemento {ele_tag}:")
    for sec_num, info in secs.items():
        print(f"    sec {sec_num} → ratio={info['ratio']:.3f}  strain={info['strain']:.2e}  loc={info['loc']:.3f}")

if not step_data:
    print("  (ningún elemento superó el umbral — verifica que el paso de análisis tenga deformación suficiente)")

print(f"\n{separador}")
print("Diagnóstico completado.")
