# OpenSees GUI Debug Script
wipe
model basic -ndm 2 -ndf 3
# Sections
section Fiber 1
patch rect 1 10 10 -0.15 -0.15 0.15 0.15
geomTransf Linear 1
# Analysis
system UmfPack
integrator LoadControl 1.0
algorithm Linear
analysis Static
analyze 1
# SUCCESS
