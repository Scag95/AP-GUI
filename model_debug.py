# Auto-generated debug script from AP-GUI
from openseespy.opensees import *

wipe()
model('basic', '-ndm', 2, '-ndf', 3)

# --- Nodes ---
node(1, 0.0, 0.0)
fix(1, 1, 1, 1)
node(2, 0.0, 3.0)
node(3, 0.0, 6.0)
node(4, 0.0, 9.0)
node(5, 0.0, 12.0)
node(6, 0.0, 15.0)
node(7, 3.0, 0.0)
fix(7, 1, 1, 1)
node(8, 3.0, 3.0)
node(9, 3.0, 6.0)
node(10, 3.0, 9.0)
node(11, 3.0, 12.0)
node(12, 3.0, 15.0)

# --- Materials ---
uniaxialMaterial('Concrete01', 1, 25000000.0, 0.0021, 5000000.0, 0.003)
uniaxialMaterial('Steel01', 2, 500000000.0, 200000000000.0, 0.01)

# --- Sections ---
section('Fiber', 10001)
patch('rect', 1, 10, 10, -0.15, -0.15, 0.15, 0.15)
layer('straight', 2, 3, 0.0003141592653589793, 0.11, -0.11, 0.11, 0.11)
layer('straight', 2, 3, 0.0003141592653589793, -0.11, -0.11, -0.11, 0.11)
uniaxialMaterial('Elastic', 20001, 750000000.0)
# Section Aggregator 1 wrapping 10001
section('Aggregator', 1, 20001, 'Vy', '-section', 10001)

# --- Transformations ---
geomTransf('Linear', 1)

# --- Elements ---
beamIntegration('Lobatto', 1, 1, 5)
element('forceBeamColumn', 1, 1, 2, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 2, 2, 3, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 3, 3, 4, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 4, 4, 5, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 5, 5, 6, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 6, 7, 8, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 7, 8, 9, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 8, 9, 10, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 9, 10, 11, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 10, 11, 12, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 11, 2, 8, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 12, 3, 9, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 13, 4, 10, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 14, 5, 11, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)
element('forceBeamColumn', 15, 6, 12, 1, 1, '-mass', 225.0, '-iter', 10, 1e-12)

# --- Patterns ---
timeSeries('Linear', 1)
pattern('Plain', 1, 1)
eleLoad('-ele', 11, '-type', '-beamUniform', -2207.25, -0.0)
eleLoad('-ele', 12, '-type', '-beamUniform', -2207.25, -0.0)
eleLoad('-ele', 13, '-type', '-beamUniform', -2207.25, -0.0)
eleLoad('-ele', 14, '-type', '-beamUniform', -2207.25, -0.0)
eleLoad('-ele', 15, '-type', '-beamUniform', -2207.25, -0.0)

# --- Gravity Analysis ---
system('UmfPack')
numberer('RCM')
constraints('Plain')
integrator('LoadControl', 0.1)
algorithm('Newton')
analysis('Static')
analyze(10)
loadConst('-time', 0.0)

# --- PUSHOVER ANALYSIS (Node 6, Dmax = 0.3, Distribución Modal)---
timeSeries('Linear', 200)
pattern('Plain', 200, 200)
load(2, 0.30252305405256186, 0.0, 0.0)
load(3, 0.8284936080365708, 0.0, 0.0)
load(4, 1.3413924157314474, 0.0, 0.0)
load(5, 1.751437342202201, 0.0, 0.0)
load(6, 1.0, 0.0, 0.0)
integrator('DisplacementControl', 6, 1, 0.003)
test('NormDispIncr', 1e-06, 100)
algorithm('KrylovNewton')
analysis('Static')
loadConst('-time', 0.0)

# --- PUSHOVER ANALYSIS (Node 6, Dmax = 0.3, Distribución Modal)---
timeSeries('Linear', 201)
pattern('Plain', 201, 201)
load(2, 0.30252305405256186, 0.0, 0.0)
load(3, 0.8284936080365708, 0.0, 0.0)
load(4, 1.3413924157314474, 0.0, 0.0)
load(5, 1.751437342202201, 0.0, 0.0)
load(6, 1.0, 0.0, 0.0)
integrator('DisplacementControl', 6, 1, 0.003)
test('NormDispIncr', 1e-06, 100)
algorithm('KrylovNewton')
analysis('Static')
loadConst('-time', 0.0)

# --- PUSHOVER ANALYSIS (Node 6, Dmax = 0.3, Distribución Modal)---
timeSeries('Linear', 202)
pattern('Plain', 202, 202)
load(2, 0.30252305405256186, 0.0, 0.0)
load(3, 0.8284936080365708, 0.0, 0.0)
load(4, 1.3413924157314474, 0.0, 0.0)
load(5, 1.751437342202201, 0.0, 0.0)
load(6, 1.0, 0.0, 0.0)
integrator('DisplacementControl', 6, 1, 0.003)
test('NormDispIncr', 1e-06, 100)
algorithm('KrylovNewton')
analysis('Static')
loadConst('-time', 0.0)

# --- PUSHOVER ANALYSIS (Node 6, Dmax = 0.3, Distribución Modal)---
timeSeries('Linear', 203)
pattern('Plain', 203, 203)
load(2, 0.30252305405256186, 0.0, 0.0)
load(3, 0.8284936080365708, 0.0, 0.0)
load(4, 1.3413924157314474, 0.0, 0.0)
load(5, 1.751437342202201, 0.0, 0.0)
load(6, 1.0, 0.0, 0.0)
integrator('DisplacementControl', 6, 1, 0.003)
test('NormDispIncr', 1e-06, 100)
algorithm('KrylovNewton')
analysis('Static')
loadConst('-time', 0.0)

# --- PUSHOVER ANALYSIS (Node 6, Dmax = 0.3, Distribución Modal)---
timeSeries('Linear', 204)
pattern('Plain', 204, 204)
load(2, 0.30252305405256186, 0.0, 0.0)
load(3, 0.8284936080365708, 0.0, 0.0)
load(4, 1.3413924157314474, 0.0, 0.0)
load(5, 1.751437342202201, 0.0, 0.0)
load(6, 1.0, 0.0, 0.0)
integrator('DisplacementControl', 6, 1, 0.003)
test('NormDispIncr', 1e-06, 100)
algorithm('KrylovNewton')
analysis('Static')
