import openseespy.opensees as ops
import sys
from pathlib import Path

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)
ops.geomTransf('PDelta', 1)
res = 'disp','vel','accel','eleResponse','forces','plasticDeformation'
ops.recorder('PVD','C:/Users/alber/OneDrive/UPM/TFM/PycharmProjects/AP-gui/Res/',*res)

# --- Outputs (Recorders) ---
ops.recorder('Node','-file','C:/Users/alber/OneDrive/UPM/TFM/PycharmProjects/AP-gui/outputs/displacement.txt','-time','-node','all','-dof',1,2,3,'disp')
ops.recorder('Node','-file','C:/Users/alber/OneDrive/UPM/TFM/PycharmProjects/AP-gui/outputs/reaction.txt','-time','-node','all','-dof',1,2,3,'reaction')
ops.recorder('Element','-file','C:/Users/alber/OneDrive/UPM/TFM/PycharmProjects/AP-gui/outputs/stresses.txt','-time','-ele','all','section','force')

# --- Materiales ---
# Hormigon C25 (tag 1)
ops.uniaxialMaterial('Concrete01', 1, 25.0, 0.002, 25.0, 0.0035)
# Acero B500S (tag 2)
ops.uniaxialMaterial('Steel01', 2, 500, 210000.0, 0.0)

# --- Secciones ---
# Viga 300×500 (secTag 1)
ops.section('Fiber', 1, '-GJ', 1000000.0)
ops.patch('rect', 1, 10, 10, -250.000000, -150.000000, 250.000000, 150.000000)
ops.layer('straight', 2, 3, 113.097336, 200.000000, -100.000000, 200.000000, 100.000000)
ops.layer('straight', 2, 4, 113.097336, -200.000000, -100.000000, -200.000000, 100.000000)
ops.beamIntegration('Lobatto',1,1,5)
# Columna 400×400 (secTag 2)
ops.section('Fiber', 2, '-GJ', 1000000.0)
ops.patch('rect', 1, 10, 10, -200.000000, -200.000000, 200.000000, 200.000000)
ops.layer('straight', 2, 4, 201.061930, 150.000000, -150.000000, 150.000000, 150.000000)
ops.layer('straight', 2, 4, 201.061930, -150.000000, -150.000000, -150.000000, 150.000000)
ops.beamIntegration('Lobatto',2,2,5)

# --- Nodos ---
# Node 1
ops.node(1, 0.0, 0.0)
# Node 2
ops.node(2, 4000.0, 0.0)
# Node 3
ops.node(3, 0.0, 4000.0)
# Node 4
ops.node(4, 4000.0, 4000.0)
# Node 5
ops.node(5, 0.0, 8000.0)
# Node 6
ops.node(6, 4000.0, 8000.0)

# --- Restricciones (fix) ---
# Fix nodo 1 (UX+UY+RZ)
ops.fix(1, 1, 1, 1)
# Fix nodo 2 (UX+UY+RZ)
ops.fix(2, 1, 1, 1)

# --- Elementos (ForceBeamColumn) ---
# FBC 1
ops.element('forceBeamColumn', 1, 1, 3, 1, 1, '-iter', 10, 1e-12, '-mass', 0.000375)
# FBC 2
ops.element('forceBeamColumn', 2, 3, 5, 1, 1, '-iter', 10, 1e-12, '-mass', 0.000375)
# FBC 3
ops.element('forceBeamColumn', 3, 2, 4, 1, 1, '-iter', 10, 1e-12, '-mass', 0.000375)
# FBC 4
ops.element('forceBeamColumn', 4, 4, 6, 1, 1, '-iter', 10, 1e-12, '-mass', 0.000375)
# FBC 5
ops.element('forceBeamColumn', 5, 3, 4, 1, 1, '-iter', 10, 1e-12, '-mass', 0.000375)
# FBC 6
ops.element('forceBeamColumn', 6, 5, 6, 1, 1, '-iter', 10, 1e-12, '-mass', 0.000375)

    # --- Aplicación de Fuerzas ---
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.eleLoad('-ele', 5, 6, '-type', '-beamUniform', -3.677494)
ops.eleLoad('-ele', 1, 2, 3, 4, '-type', '-beamUniform', 0, -3.677494)

ops.eigen(3)
    # --- Configuración del Análisis ---
ops.system('UmfPack')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 0.1)
ops.algorithm('Newton')
ops.analysis('Static')
ops.analyze(10)

print('Análisis de gravedad completado con éxito')


# ======================================================
# Análisis Pushover
# ======================================================
# NOTA: Este script asume que el modelo ya está construido
# y el análisis de gravedad ya se ejecutó.
#
# Ejecuta primero: gravity_analysis.py
# ======================================================


# --- Definición de Estructura para Resultados por Piso ---
floor_nodes = {0: [1, 2], 1: [3, 4], 2: [5, 6]}
story_columns = {1: [1, 3], 2: [2, 4]}

# Fijar cargas de gravedad
ops.loadConst('-time', 0.0)

# --- Configuración y Ejecución del Pushover ---
story_drifts_history = {}
story_shears_history = {}

# ======================================================
# Análisis Pushover
# ======================================================
import openseespy.opensees as ops

# Definir TimeSeries y Pattern para Pushover
ops.timeSeries('Linear', 2)
ops.pattern('Plain', 2, 2)

# --- Patrón de Carga Uniforme ---
# Se aplica una fuerza unitaria en el primer nodo de cada nivel (excepto base)
ops.load(3, 1.0, 0.0, 0.0) # Nivel Y=4000.0
ops.load(5, 1.0, 0.0, 0.0) # Nivel Y=8000.0

# 1. Configuración del análisis
ops.wipeAnalysis()
ops.system('UmfPack')
ops.numberer('RCM')
ops.constraints('Plain')

# 2. Parámetros de control
ctrlNode = 5
ctrlDOF = 1
maxU = 160.0
dU = 1.0
nSteps = int(maxU / dU)

# 3. Integrador y Test
ops.integrator('DisplacementControl', ctrlNode, ctrlDOF, dU)
ops.test('NormDispIncr', 1e-06, 100)
ops.algorithm('KrylovNewton')
ops.analysis('Static')

# 4. Loop de análisis
baseShear = []
roofDisp = []

for i in range(nSteps):
    ok = ops.analyze(1)
    if ok != 0:
        print(f'Fallo de convergencia en el paso {i}')
        break

    # Cortante basal
    Vb = 0.0
    support_nodes = [1, 2]
    for nd in support_nodes:
        try:
            ops.reactions()
            Vb += ops.nodeReaction(nd, 1)
        except:
            pass
    baseShear.append(-Vb)

    # Resultados
    try:
        u = ops.nodeDisp(ctrlNode, ctrlDOF)
    except:
        u = 0.0
    roofDisp.append(u)

    # --- Cálculo de Drifts y Cortantes de Piso ---
    for story_idx, nodes in floor_nodes.items():
        if story_idx == 0: continue
        # Drift
        top_nodes = floor_nodes[story_idx]
        bot_nodes = floor_nodes[story_idx-1]
        u_top = sum([ops.nodeDisp(n, 1) for n in top_nodes]) / len(top_nodes)
        u_bot = sum([ops.nodeDisp(n, 1) for n in bot_nodes]) / len(bot_nodes)
        drift = u_top - u_bot
        story_drifts_history.setdefault(story_idx, []).append(drift)
        
        # Shear
        v_story = 0.0
        if story_idx in story_columns:
            for ele in story_columns[story_idx]:
                try:
                    # ForceBeamColumn 2D: [P1, V1, M1, P2, V2, M2]
                    # Cortante en nodo i (base de la columna) es index 1
                    forces = ops.eleResponse(ele, 'force')
                    v_story += forces[1]
                except:
                    pass
        story_shears_history.setdefault(story_idx, []).append(-v_story) # Signo?

    print(f'Paso {i}: Desp={u:.4f}, Vb={-Vb:.4f}')

print('Análisis finalizado')
# ======================================================
# Guardar datos para gráfica
# ======================================================
import json
import os
if not os.path.exists('outputs'):
    os.makedirs('outputs')
output_data = {
    'story_drifts': story_drifts_history,
    'story_shears': story_shears_history,
    'roof_displacement': roofDisp,
    'base_shear': baseShear
}
with open('outputs/pushover_curve.json', 'w') as f:
    json.dump(output_data, f, indent=4)
print('Datos de curva pushover guardados en outputs/pushover_curve.json')

print('Análisis Pushover completado')