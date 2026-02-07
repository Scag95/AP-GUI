from src.analysis.model_builder import ModelBuilder
from src.analysis.solvers.gravity_solver import GravitySolver
from src.analysis.solvers.pushover_solver import PushoverSolver
import openseespy.opensees as ops

class OpenSeesTranslator:
    """
    Facade class that orchestrates the Model Building and Analysis execution.
    Delegates complex logic to specialized solvers.
    Keeps the same public API as before to avoid breaking UI.
    """
    def __init__(self):
        self.builder = ModelBuilder()
        self.gravity_solver = GravitySolver(self.builder)
        self.pushover_solver = PushoverSolver(self.builder)

    def build_model(self):
        """Delegates model construction to ModelBuilder."""
        return self.builder.build_model()
        
    def run_gravity_analysis(self):
        """Delegates gravity analysis to GravitySolver."""
        return self.gravity_solver.run()
        
    def get_analysis_results(self):
        """Delegates result extraction to GravitySolver."""
        return self.gravity_solver.get_results()
        
    def run_pushover_analysis(self, control_node_tag, max_disp, load_pattern_type, n_steps = 100):
        """Delegates pushover analysis to PushoverSolver."""
        return self.pushover_solver.run_pushover(control_node_tag, max_disp, load_pattern_type, n_steps)
        
    def run_modal_analysis(self, n_modes):
        """Delegates modal analysis to PushoverSolver (where it was moved)."""
        return self.pushover_solver.run_modal_analysis(n_modes)
        
    def dump_model_to_file(self, filename="model_dump.out"):
        """Direct OpenSees dump."""
        ops.printModel('-file', filename)
        print(f"[OpenSees] Modelo volcado en: {filename}")

        
    def run_adaptive_pushover(self, control_node_tag, max_disp, load_pattern_type):
        return self.pushover_solver.run_adaptative_pushover(control_node_tag, max_disp, load_pattern_type)