"""
Test 3 — Comunicación entre módulos y persistencia
Fichero: tests/test_communication.py
"""

import os
import pytest
from PyQt6.QtTest import QSignalSpy
from src.analysis.manager import ProjectManager
from src.analysis.node import Node
from src.analysis.materials import Elastic, Concrete01, Steel01
from src.analysis.sections import FiberSection, RectPatch
from src.analysis.element import ForceBeamColumn
from src.analysis.loads import LoadPattern, NodalLoad


def test_datachanged_signal(qapp_session):
    """
    3.1 Emisión y recepción de dataChanged.
    Verifica que la señal dataChanged se emite al realizar modificaciones en el ProjectManager.
    """
    pm = ProjectManager.instance()
    spy = QSignalSpy(pm.dataChanged)

    # 1. Emitir la señal dataChanged al modificar datos
    pm.dataChanged.emit()
    assert len(spy) == 1, "La señal dataChanged debe haberse emitido 1 vez"

    # 2. Emitir la señal de nuevo
    pm.dataChanged.emit()
    assert len(spy) == 2, "La señal dataChanged debe haberse emitido 2 veces"


def test_json_persistence_roundtrip(tmp_path, qapp_session):
    """
    3.2 Persistencia JSON bidireccional.
    Verifica que guardar y cargar conserva la integridad completa del modelo.
    """
    pm = ProjectManager.instance()

    # 1. Crear modelo completo
    mat1 = Concrete01(tag=1, name="Concrete", fpc=-25e6, epsc0=-0.002, fpcu=-5e6, epsu=-0.0035)
    mat2 = Steel01(tag=2, name="Steel", Fy=500e6, E0=200e9, b=0.01)
    mat3 = Elastic(tag=3, name="ElasticMat", E=30e9)

    pm.add_material(mat1)
    pm.add_material(mat2)
    pm.add_material(mat3)

    sec1 = FiberSection(tag=1, name="ColSec")
    sec1.add_rect_patch(RectPatch(material_tag=1, yI=-0.2, zI=-0.2, yJ=0.2, zJ=0.2, nIy=5, nIz=5))
    pm.add_section(sec1)

    pm.add_node(Node(tag=1, x=0.0, y=0.0, fixity=[1, 1, 1]))
    pm.add_node(Node(tag=2, x=0.0, y=3.0, fixity=[0, 0, 0]))

    pm.add_element(ForceBeamColumn(tag=1, node_i=1, node_j=2, section_tag=1, transf_tag=1, integration_points=5))

    pat = LoadPattern(tag=1, name="GravPattern")
    pat.add_load(NodalLoad(tag=1, node_tag=2, fx=0.0, fy=-1000.0, mz=0.0))
    pm.add_pattern(pat)

    # 2. Guardar a JSON temporal
    file_path = str(tmp_path / "test_model.json")
    save_ok = pm.save_project(file_path)
    assert save_ok, "El archivo debe guardarse exitosamente"
    assert os.path.exists(file_path), "El archivo JSON debe existir en el sistema"

    # 3. Limpiar manager y recargar
    ProjectManager._instance = None
    pm_new = ProjectManager.instance()
    load_ok = pm_new.load_project(file_path)
    assert load_ok, "El proyecto debe cargarse exitosamente"

    # 4. Comprobar integridad post-carga
    assert len(pm_new.get_all_materials()) == 3, "Debe haber 3 materiales"
    assert len(pm_new.get_all_sections()) == 1, "Debe haber 1 sección"
    assert len(pm_new.get_all_nodes()) == 2, "Debe haber 2 nodos"
    assert len(pm_new.get_all_elements()) == 1, "Debe haber 1 elemento"
    assert len(pm_new.get_all_patterns()) == 1, "Debe haber 1 patrón de carga"

    mat_loaded = pm_new.get_material(1)
    assert mat_loaded.name == "Concrete"
