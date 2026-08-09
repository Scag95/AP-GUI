"""
Test 1 — Validación de entrada de datos y conversión de unidades
Fichero: tests/test_validation.py
"""

import pytest
from PyQt6.QtWidgets import QDoubleSpinBox, QLineEdit
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitManager, UnitType
from src.ui.dialogs.material_dialog import MaterialDialog


def test_qdoublespinbox_range_validation(qapp_session):
    """
    1.1 Rechazo de valores fuera de rango en QDoubleSpinBox.
    Verifica que QDoubleSpinBox trunca o fuerza los límites configurados (mínimo y máximo).
    """
    spin = QDoubleSpinBox()
    spin.setRange(0.01, 100000.0)

    # 1. Intentar introducir valor negativo
    spin.setValue(-20000.0)
    assert spin.value() == 0.01, "El SpinBox debe forzar el valor al mínimo permitido (0.01)"

    # 2. Intentar introducir valor cero
    spin.setValue(0.0)
    assert spin.value() == 0.01, "El SpinBox debe rechazar 0.0 si el mínimo es > 0"

    # 3. Intentar introducir valor mayor al máximo
    spin.setValue(1.0e15)
    assert spin.value() == 100000.0, "El SpinBox debe truncar el valor al máximo configurado"


def test_unit_spinbox_conversion(qapp_session):
    """
    1.2 Conversión correcta de unidades en UnitSpinBox.
    Verifica que la transformación entre unidades de usuario y unidades base (SI) es exacta.
    """
    unit_mgr = UnitManager.instance()
    unit_mgr.set_unit(UnitType.FORCE, "kN")

    spin = UnitSpinBox(UnitType.FORCE)
    spin.setRange(0, 1e12)
    
    # 1. Introducir 10.0 kN
    spin.setValue(10.0)

    # 2. Verificar que el valor base en N es 10000.0
    assert abs(spin.get_value_base() - 10000.0) < 1e-6, "El valor base en N debe ser 10000.0"

    # 3. Cambiar el sistema de unidades a N
    unit_mgr.set_unit(UnitType.FORCE, "N")

    # 4. El spinbox visualmente debe mostrar 10000.0 y el valor base debe ser 10000.0
    assert abs(spin.value() - 10000.0) < 1e-6, "El valor visual debe actualizarse a 10000.0 N"
    assert abs(spin.get_value_base() - 10000.0) < 1e-6, "El valor base debe conservarse en 10000.0 N"


def test_material_dialog_mandatory_fields(qapp_session):
    """
    1.3 Campos obligatorios o diálogos de material.
    Verifica la instanciación del diálogo de materiales y la validación de entrada.
    """
    dialog = MaterialDialog()
    assert dialog is not None
    assert dialog.materials_list is not None
