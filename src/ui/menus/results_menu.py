from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from src.ui.dialogs.pushover_result_dialog import PushoverResultsWidget
from src.ui.dialogs.pushover_log_dialog import PushoverLogDialog
from src.ui.dialogs.moment_curvature_dialog import MomentCurvatureWidget
from src.ui.dialogs.fiber_strain_dialog import FiberStrainDialog
from src.analysis.manager import ProjectManager


class ResultsMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__("Resultados", parent)

        act = QAction("Deformada", self)
        act.triggered.connect(lambda: self._set_deformed_visibility(True))
        self.addAction(act)

        self.addSeparator()

        act_m = QAction("Momentos (M)", self)
        act_m.triggered.connect(lambda: self._show_diagram("M"))
        self.addAction(act_m)

        act_v = QAction("Cortantes (V)", self)
        act_v.triggered.connect(lambda: self._show_diagram("V"))
        self.addAction(act_v)

        act_p = QAction("Axiales (P)", self)
        act_p.triggered.connect(lambda: self._show_diagram("P"))
        self.addAction(act_p)

        self.addSeparator()

        act_push = QAction("Curva Pushover", self)
        act_push.triggered.connect(self._show_curve_pushover)
        self.addAction(act_push)

        act_log = QAction("Ver Logs del Último Pushover", self)
        act_log.triggered.connect(self._show_pushover_logs)
        self.addAction(act_log)

        act_sec = QAction("Análisis de Sección (M-phi)", self)
        act_sec.triggered.connect(self._show_section_results)
        self.addAction(act_sec)

        act_fiber = QAction("Deformaciones de Fibras", self)
        act_fiber.triggered.connect(self._show_fiber_strains)
        self.addAction(act_fiber)

        self.addSeparator()

        act_clear = QAction("Ocultar Resultados", self)
        act_clear.triggered.connect(self._clear_results)
        self.addAction(act_clear)

    def _set_deformed_visibility(self, visible):
        if self.parent() and hasattr(self.parent(), "viz_widget"):
            self.parent().viz_widget.set_visibility("deformed", visible)

    def _clear_results(self):
        if self.parent() and hasattr(self.parent(), "_viewports"):
            for viz in self.parent()._viewports:
                viz.show_force_diagrams(None)
                viz.set_visibility("deformed", False)

    def _show_diagram(self, type_):
        if self.parent() and hasattr(self.parent(), "viz_widget"):
            self.parent().viz_widget.show_force_diagrams(type_)

    def _show_curve_pushover(self):
        results = ProjectManager.instance().pushover_results
        if not results:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No hay resultados",
                               "Debe ejecutar primero un Análisis Pushover.")
            return
        widget = PushoverResultsWidget(results)
        self.parent().add_tool_window(widget, "Curva de Capacidad (Pushover)")

    def _show_pushover_logs(self):
        log_text = getattr(ProjectManager.instance(), "pushover_log_text", None)
        if not log_text:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Sin logs",
                                    "Aún no se ha ejecutado ningún análisis pushover.")
            return
        dialog = PushoverLogDialog(log_text, self.parent())
        dialog.exec()

    def _show_section_results(self):
        widget = MomentCurvatureWidget()
        self.parent().add_tool_window(widget, "Análisis de sección: Momento-Curvatura")

    def _show_fiber_strains(self):
        widget = FiberStrainDialog()
        self.parent().add_tool_window(widget, "Deformaciones de Fibras")
        if hasattr(self.parent(), 'anim_toolbar'):
            widget.connect_to_animation(self.parent().anim_toolbar)
