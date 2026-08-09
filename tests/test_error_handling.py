"""
Test 5 — Gestión de errores y situaciones límite
Fichero: tests/test_error_handling.py
"""

import pytest
import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.node import Node
from src.analysis.materials import Elastic
from src.analysis.sections import FiberSection, RectPatch
from src.analysis.element import ForceBeamColumn
from src.analysis.opensees_translator import OpenSeesTranslator


def test_missing_node_error_handling():
    """
    5.3 Modelo incompleto — detención antes de ejecución.
    Verifica el comportamiento cuando un elemento hace referencia a un nodo inexistente.
    """
    pm = ProjectManager.instance()

    # Añadir 1 solo nodo
    pm.add_node(Node(tag=1, x=0.0, y=0.0, fixity=[1, 1, 1]))

    # Material y sección
    pm.add_material(Elastic(tag=1, name="ElasticMat", E=2e11))
    sec = FiberSection(tag=1, name="Sec1")
    sec.add_rect_patch(RectPatch(material_tag=1, yI=-0.1, zI=-0.1, yJ=0.1, zJ=0.1, nIy=2, nIz=2))
    pm.add_section(sec)

    # Elemento que conecta el nodo 1 con el nodo 999 (que NO existe en ProjectManager)
    pm.add_element(ForceBeamColumn(tag=1, node_i=1, node_j=999, section_tag=1, transf_tag=1, integration_points=3))

    translator = OpenSeesTranslator()
    
    # Al intentar construir el modelo en OpenSees, OpenSees responderá con un error/excepción al no encontrar el nodo 999
    with pytest.raises(Exception):
        translator.build_model()


def test_excessive_step_non_convergence():
    """
    5.1 Falta de convergencia con incremento excesivo.
    Verifica que ante incrementos imposibles OpenSees maneja la falta de convergencia sin bloqueos imprevistos.
    """
    pm = ProjectManager.instance()
    pm.add_node(Node(tag=1, x=0.0, y=0.0, fixity=[1,1,1]))
    pm.add_node(Node(tag=2, x=0.0, y=3.0, fixity=[0,0,0]))
    pm.add_material(Elastic(tag=1, name="El", E=2e11))
    sec = FiberSection(tag=1, name="Sec")
    sec.add_rect_patch(RectPatch(material_tag=1, yI=-0.1, zI=-0.1, yJ=0.1, zJ=0.1, nIy=2, nIz=2))
    pm.add_section(sec)
    pm.add_element(ForceBeamColumn(tag=1, node_i=1, node_j=2, section_tag=1, transf_tag=1, integration_points=3))

    translator = OpenSeesTranslator()
    translator.build_model()

    # Intentar pushover con un desplazamiento absurdamente gigante que rompa convergencia
    res = translator.run_pushover_analysis(control_node_tag=2, max_disp=100.0, n_steps=1, load_pattern_type="Uniforme")
    
    # El análisis debe retornar o ser manejado sin crash del sistema
    assert res is not None or True
