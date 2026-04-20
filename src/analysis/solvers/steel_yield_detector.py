import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge

class SteelYieldDetector:

    def __init__(self):
        self.manager = ProjectManager.instance()

    def capture_step(self) -> dict:
        """
        Devuelve la fibra de acero con mayor ratio de fluencia por sección y elemento.
        { ele_tag: { sec_num: { "ratio": float, "strain": float, "mat_tag": int } } }
        """
        step_data = {}

        for ele in self.manager.get_all_elements():
            if not isinstance(ele, (ForceBeamColumn, ForceBeamColumnHinge)):
                continue

            ele_data = {}

            for sec_num in range(1, ele.integration_points + 1):
                try:
                    fiber_data = ops.eleResponse(ele.tag, 'section', sec_num, 'fiberData')
                except Exception:
                    continue

                if not fiber_data:
                    continue

                max_ratio  = 0.0
                max_strain = 0.0

                # fiberData: bloques de 6 → [y, z, area, matTag, stress, strain]
                for idx in range(0, len(fiber_data) - 5, 6):
                    mat_tag = int(fiber_data[idx + 3])
                    strain  = fiber_data[idx + 5]

                    mat = self.manager.get_material(mat_tag)
                    if mat is None:
                        continue

                    eps_y = mat.get_yield_strain()
                    if eps_y is None or eps_y <= 0:
                        continue

                    ratio = abs(strain) / eps_y
                    if ratio > max_ratio:
                        max_ratio  = ratio
                        max_strain = strain

                if max_ratio > 0:
                    try:
                        loc = ops.sectionLocation(ele.tag, sec_num)
                    except Exception:
                        loc = (sec_num - 1) / max(ele.integration_points - 1, 1)

                    ele_data[sec_num] = {
                        "ratio":  max_ratio,
                        "strain": max_strain,
                        "loc":    loc
                    }

            if ele_data:
                step_data[ele.tag] = ele_data

        return step_data
