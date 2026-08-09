import pytest
from PyQt6.QtWidgets import QApplication
from src.analysis.manager import ProjectManager
import openseespy.opensees as ops

@pytest.fixture(scope="session")
def qapp_session():
    """Fixture de sesión para la aplicación PyQt6."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture(autouse=True)
def reset_project_manager():
    """Fixture que reinicia el Singleton de ProjectManager y limpia OpenSees antes de cada test."""
    ProjectManager._instance = None
    pm = ProjectManager.instance()
    try:
        ops.wipe()
    except Exception:
        pass
    yield pm
    ProjectManager._instance = None
    try:
        ops.wipe()
    except Exception:
        pass
