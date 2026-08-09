"""
Test 2 — Motor de cálculo y traducción al dominio de OpenSees
Fichero: tests/test_engine.py
"""

import pytest
import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.node import Node
from src.analysis.materials import Elastic
from src.analysis.sections import FiberSection, RectPatch
from src.analysis.element import ForceBeamColumn
from src.analysis.loads import NodalLoad, LoadPattern
from src.analysis.opensees_translator import OpenSeesTranslator


def test_cantilever_beam_analytical():
    """
    2.1 Viga empotrada con carga puntual.
    Compara la solución de OpenSees con la solución analítica: δ = P*L^3 / (3*E*I).
    """
    pm = ProjectManager.instance()

    # Geometría y propiedades
    L = 5.0          # m
    b = 0.3          # m
    h = 0.5          # m
    E = 30.0e9       # Pa (30 GPa)
    P = 10000.0      # N
    I = (b * (h ** 3)) / 12.0  # 0.003125 m4

    delta_analytical = (P * (L ** 3)) / (3.0 * E * I)  # ~0.0044444... m

    # 1. Crear nodos
    n1 = Node(tag=1, x=0.0, y=0.0, fixity=[1, 1, 1])
    n2 = Node(tag=2, x=L,   y=0.0, fixity=[0, 0, 0])
    pm.add_node(n1)
    pm.add_node(n2)

    # 2. Material y Sección
    mat = Elastic(tag=1, name="ConcreteElastic", E=E)
    pm.add_material(mat)

    sec = FiberSection(tag=1, name="BeamSec")
    sec.add_rect_patch(RectPatch(material_tag=1, yI=-h/2, zI=-b/2, yJ=h/2, zJ=b/2, nIy=10, nIz=10))
    pm.add_section(sec)

    # 3. Elemento
    ele = ForceBeamColumn(tag=1, node_i=1, node_j=2, section_tag=1, transf_tag=1, integration_points=5)
    pm.add_element(ele)

    # 4. Carga puntual en nodo 2 (Fy = -10000 N)
    pat = LoadPattern(tag=1, name="GravityPattern")
    pat.add_load(NodalLoad(tag=1, node_tag=2, fx=0.0, fy=-P, mz=0.0))
    pm.add_pattern(pat)

    # 5. Ejecutar análisis
    translator = OpenSeesTranslator()
    translator.build_model()
    translator.run_gravity_analysis()

    # 6. Extraer desplazamiento vertical del nodo 2
    disp_y = ops.nodeDisp(2, 2)
    disp_y_abs = abs(disp_y)

    rel_error = abs(disp_y_abs - delta_analytical) / delta_analytical
    assert rel_error <= 0.025, f"Error relativo en desplazamiento ({rel_error}) excede tolerancia 0.025"


def test_elastic_frame_lateral_load():
    """
    2.2 Pórtico elástico con carga lateral.
    Resuelve un pórtico simple de 1 vano y 1 piso con carga lateral y verifica respuesta elástica.
    """
    pm = ProjectManager.instance()
    H = 3.0
    L = 6.0
    E = 30.0e9
    P = 5000.0

    # Nodos
    pm.add_node(Node(tag=1, x=0.0, y=0.0, fixity=[1, 1, 1]))
    pm.add_node(Node(tag=2, x=L,   y=0.0, fixity=[1, 1, 1]))
    pm.add_node(Node(tag=3, x=0.0, y=H,   fixity=[0, 0, 0]))
    pm.add_node(Node(tag=4, x=L,   y=H,   fixity=[0, 0, 0]))

    # Material y sección
    pm.add_material(Elastic(tag=1, name="ElasticMat", E=E))
    sec = FiberSection(tag=1, name="SquareSec")
    sec.add_rect_patch(RectPatch(material_tag=1, yI=-0.2, zI=-0.2, yJ=0.2, zJ=0.2, nIy=8, nIz=8))
    pm.add_section(sec)

    # Elementos (Columnas 1,2; Viga 3)
    pm.add_element(ForceBeamColumn(tag=1, node_i=1, node_j=3, section_tag=1, transf_tag=1, integration_points=5))
    pm.add_element(ForceBeamColumn(tag=2, node_i=2, node_j=4, section_tag=1, transf_tag=1, integration_points=5))
    pm.add_element(ForceBeamColumn(tag=3, node_i=3, node_j=4, section_tag=1, transf_tag=1, integration_points=5))

    # Carga lateral en nodo 3
    pat = LoadPattern(tag=1, name="LateralPattern")
    pat.add_load(NodalLoad(tag=1, node_tag=3, fx=P, fy=0.0, mz=0.0))
    pm.add_pattern(pat)

    translator = OpenSeesTranslator()
    translator.build_model()
    translator.run_gravity_analysis()

    disp_x3 = ops.nodeDisp(3, 1)
    disp_x4 = ops.nodeDisp(4, 1)

    assert disp_x3 > 0, "El nodo 3 debe desplazarse en la dirección positiva X"
    assert abs(disp_x3 - disp_x4) / disp_x3 < 0.05, "El desplazamiento del techo debe ser consistente entre nodos"


def test_model_builder_tag_uniqueness():
    """
    2.3 Unicidad de tags en ModelBuilder.
    Verifica que ModelBuilder construye sin colisiones de identificadores.
    """
    pm = ProjectManager.instance()
    
    # Crear material y sección
    pm.add_material(Elastic(tag=1, name="Mat1", E=2.0e11))
    sec = FiberSection(tag=1, name="Sec1")
    sec.add_rect_patch(RectPatch(material_tag=1, yI=-0.1, zI=-0.1, yJ=0.1, zJ=0.1, nIy=4, nIz=4))
    pm.add_section(sec)

    # Nodos
    for i in range(1, 51):
        pm.add_node(Node(tag=i, x=float(i), y=0.0, fixity=[1,1,1] if i==1 else [0,0,0]))

    # Elementos
    for i in range(1, 50):
        pm.add_element(ForceBeamColumn(tag=i, node_i=i, node_j=i+1, section_tag=1, transf_tag=1, integration_points=3))

    translator = OpenSeesTranslator()
    # Construcción sin excepciones por colisión
    translator.build_model()
    assert True
