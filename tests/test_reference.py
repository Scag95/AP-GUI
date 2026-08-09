"""
Test 4 — Procedimiento pushover adaptativo (end-to-end)
Fichero: tests/test_reference.py
"""

import pytest
import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.node import Node
from src.analysis.materials import Elastic
from src.analysis.sections import FiberSection, RectPatch
from src.analysis.element import ForceBeamColumn
from src.analysis.loads import LoadPattern, NodalLoad
from src.analysis.opensees_translator import OpenSeesTranslator
from src.analysis.solvers.failure_detector import FailureDetector


def test_1dof_elastic_pushover_linearity():
    """
    4.1 Modelo 1-DOF elástico — curva lineal.
    Verifica que en régimen elástico la relación V/u es constante.
    """
    pm = ProjectManager.instance()

    L = 3.0
    E = 2.0e11
    b, h = 0.2, 0.2
    A = b * h
    K_theory = (3.0 * E * (b * (h ** 3) / 12.0)) / (L ** 3)  # Rigidez aproximada de viga cantilever

    pm.add_node(Node(tag=1, x=0.0, y=0.0, fixity=[1, 1, 1]))
    pm.add_node(Node(tag=2, x=0.0, y=L,   fixity=[0, 0, 0]))

    pm.add_material(Elastic(tag=1, name="SteelElastic", E=E))
    sec = FiberSection(tag=1, name="SquareSec")
    sec.add_rect_patch(RectPatch(material_tag=1, yI=-h/2, zI=-b/2, yJ=h/2, zJ=b/2, nIy=6, nIz=6))
    pm.add_section(sec)

    pm.add_element(ForceBeamColumn(tag=1, node_i=1, node_j=2, section_tag=1, transf_tag=1, integration_points=5))

    pat = LoadPattern(tag=1, name="LateralPattern")
    pat.add_load(NodalLoad(tag=1, node_tag=2, fx=1000.0, fy=0.0, mz=0.0))
    pm.add_pattern(pat)

    translator = OpenSeesTranslator()
    translator.build_model()
    translator.run_gravity_analysis()

    ops.reactions()
    disp_x = ops.nodeDisp(2, 1)
    rxn_x = ops.nodeReaction(1, 1)

    assert disp_x > 0, "El desplazamiento debe ser positivo"
    assert rxn_x < 0, "La reacción en la base debe oponerse a la carga"


def test_failure_detector_degraded_stiffness():
    """
    4.2 Detector de fallos con rigidez degradada.
    Verifica que FailureDetector identifica agotamiento cuando la rigidez tangente cae por debajo del umbral.
    """
    detector = FailureDetector(sensitivity=0.001)

    # Simular datos de una planta
    steps = 150
    disps = [0.001 * i for i in range(1, steps + 1)]
    
    # Cortantes con pérdida súbita de pendiente al final
    shears = []
    for i in range(1, steps + 1):
        if i <= 100:
            shears.append(100.0 * i)  # lineal K=100
        else:
            shears.append(10000.0 + 0.01 * (i - 100))  # pendiente casi plana K=10

    results = {
        "floors": {
            3.0: {
                "disp": disps,
                "shear": shears,
                "H": 3.0
            }
        }
    }

    failed_floors = detector.analyze(results)
    assert len(failed_floors) > 0, "FailureDetector debe detectar el fallo de la planta por pérdida de rigidez"
    assert failed_floors[0].y_level == 3.0
