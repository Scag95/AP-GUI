# Auto-generated debug script from AP-GUI
from openseespy.opensees import *

wipe()
model('basic', '-ndm', 2, '-ndf', 3)

# --- Nodes ---
node(1, 0.0, 0.0)
fix(1, 1, 1, 1)
node(2, 0.0, 3.5)
node(3, 0.0, 7.0)
node(4, 0.0, 10.5)
node(5, 3.0, 0.0)
fix(5, 1, 1, 1)
node(6, 3.0, 3.5)
node(7, 3.0, 7.0)
node(8, 3.0, 10.5)

# --- Materials ---
# Material Elastico R�gido para Congelaciones adaptativas
uniaxialMaterial('Elastic', 99999, 1000000000000.0)
uniaxialMaterial('Concrete01', 1, 25000000.0, 0.002, 25000000.0, 0.0035)
uniaxialMaterial('Steel01', 2, 500000000.0, 200000000000.0, 1e-06, 0.0, 0.0, 0.0, 0.0)

# --- Sections ---
section('Fiber', 10001)
patch('rect', 1, 10, 10, -0.15, -0.1, 0.15, 0.1)
layer('straight', 2, 3, 0.0003141592653589793, 0.11, -0.06, 0.11, 0.06)
layer('straight', 2, 3, 0.0003141592653589793, -0.11, -0.06, -0.11, 0.06)
uniaxialMaterial('Elastic', 20001, 500000000.0)
# Section Aggregator 1 wrapping 10001
section('Aggregator', 1, 20001, 'Vy', '-section', 10001)
section('Fiber', 10002)
patch('rect', 1, 10, 10, -0.2, -0.2, 0.2, 0.2)
layer('straight', 2, 4, 0.0003141592653589793, 0.16, -0.16, 0.16, 0.16)
layer('straight', 2, 4, 0.0003141592653589793, -0.16, -0.16, -0.16, 0.16)
layer('straight', 2, 2, 0.0003141592653589793, 0.053333, -0.16, -0.053333, -0.16)
layer('straight', 2, 2, 0.0003141592653589793, 0.053333, 0.16, -0.053333, 0.16)
uniaxialMaterial('Elastic', 20002, 1333333333.3333335)
# Section Aggregator 2 wrapping 10002
section('Aggregator', 2, 20002, 'Vy', '-section', 10002)

# --- Transformations ---
geomTransf('PDelta', 1)

# --- Elements ---
beamIntegration('Lobatto', 1, 2, 6)
element('forceBeamColumn', 1, 1, 2, 1, 1, '-mass', 400.00000000000006, '-iter', 10, 1e-12)
element('forceBeamColumn', 2, 2, 3, 1, 1, '-mass', 400.00000000000006, '-iter', 10, 1e-12)
element('forceBeamColumn', 3, 3, 4, 1, 1, '-mass', 400.00000000000006, '-iter', 10, 1e-12)
element('forceBeamColumn', 4, 5, 6, 1, 1, '-mass', 400.00000000000006, '-iter', 10, 1e-12)
element('forceBeamColumn', 5, 6, 7, 1, 1, '-mass', 400.00000000000006, '-iter', 10, 1e-12)
element('forceBeamColumn', 6, 7, 8, 1, 1, '-mass', 400.00000000000006, '-iter', 10, 1e-12)
beamIntegration('Lobatto', 2, 1, 6)
element('forceBeamColumn', 7, 2, 6, 1, 2, '-mass', 150.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 8, 3, 7, 1, 2, '-mass', 150.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 9, 4, 8, 1, 2, '-mass', 150.0, '-iter', 10, 1e-12)

# --- Patterns ---
timeSeries('Linear', 1)
pattern('Plain', 1, 1)

# --- Gravity Analysis ---
system('UmfPack')
numberer('RCM')
constraints('Plain')
integrator('LoadControl', 0.1)
algorithm('Newton')
analysis('Static')
analyze(10)
loadConst('-time', 0.0)


# ====== CONFIGURACION DE PUSHOVER ======

# --- Anañysis Modal --- 
eigen(1)
timeSeries('Linear', 200)
pattern('Plain', 200, 200)
load(2, 0.5386090327719475, 0.0, 0.0)
load(3, 1.3825244870144129, 0.0, 0.0)
load(4, 1.0, 0.0, 0.0)
wipeAnalysis()
system('UmfPack')
numberer('RCM')
constraints('Transformation')
integrator('DisplacementControl', 4, 1, 0.001)
test('NormDispIncr', 1e-06, 100)
algorithm('KrylovNewton')
analysis('Static')


uniaxialMaterial('Elastic', 999999, 10000000000.0)
node(2000020, 0.0, 3.5)
fix(2000020, 1, 1, 1)

element('zeroLength', 3000020, 2000020, 2, '-mat', 999999, '-dir', 1)
node(2000060, 3.0, 3.5)
fix(2000060, 1, 1, 1)

element('zeroLength', 3000060, 2000060, 6, '-mat', 999999, '-dir', 1)


loadConst('-time', 0.0)
timeSeries('Linear', 201)
pattern('Plain', 201, 201)
load(2, 0.5386090327719475, 0.0, 0.0)
load(3, 1.3825244870144129, 0.0, 0.0)
load(4, 1.0, 0.0, 0.0)
wipeAnalysis()
system('UmfPack')
numberer('RCM')
constraints('Transformation')
integrator('DisplacementControl', 4, 1, 0.001)
test('NormDispIncr', 1e-06, 100)
algorithm('KrylovNewton')
analysis('Static')
uniaxialMaterial('Elastic', 999999, 10000000000.0)
node(2000030, 0.0, 7.0)
fix(2000030, 1, 1, 1)
element('zeroLength', 3000030, 2000030, 3, '-mat', 999999, '-dir', 1)
node(2000070, 3.0, 7.0)
fix(2000070, 1, 1, 1)
element('zeroLength', 3000070, 2000070, 7, '-mat', 999999, '-dir', 1)
loadConst('-time', 0.0)
timeSeries('Linear', 202)
pattern('Plain', 202, 202)
load(2, 0.5386090327719475, 0.0, 0.0)
load(3, 1.3825244870144129, 0.0, 0.0)
load(4, 1.0, 0.0, 0.0)
wipeAnalysis()
system('UmfPack')
numberer('RCM')
constraints('Transformation')
integrator('DisplacementControl', 4, 1, 0.001)
test('NormDispIncr', 1e-06, 100)
algorithm('KrylovNewton')
analysis('Static')
