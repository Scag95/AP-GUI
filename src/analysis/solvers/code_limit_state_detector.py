import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
from src.analysis.sections import FiberSection, AggregatorSection
from src.analysis.materials import Steel01, Concrete01


class CodeLimitStateDetector:
    """
    Detecta el primer desplazamiento de cubierta (roof_disp) en que cada planta
    supera los estados límite DL / SL / NC según EC8.

    FiberSection → Steel01 activa DL; Concrete01 activa SL/NC (0.75/1.25 × εcu).
    AggregatorSection → material Mz (Hysteretic/HystereticSM): e1→DL, e2→SL, e3→NC.
    """

    EPSC_U    = 0.0035   # deformación última del hormigón (EC8)
    SL_FACTOR = 0.75
    NC_FACTOR = 1.25

    def __init__(self):
        self.manager = ProjectManager.instance()
        self._results: dict = {}
        self._elem_floor_map: dict = {}
        self._pre_existing: set = set()
        self.reset()

    # ─── API pública ──────────────────────────────────────────────────────────

    def reset(self):
        self._results = {}
        self._elem_floor_map = {}
        self._pre_existing = set()
        self._build_maps()

    def capture_baseline(self):
        """
        Llama justo antes del primer paso del pushover (modelo en estado de gravedad).
        Registra qué (ele, sec_num, LS) ya están superados — granularidad por sección,
        no por planta, para que secciones nuevas que crucen DL durante el pushover
        sí activen el marcador aunque otras en la misma planta ya lo tuvieran.
        """
        self._pre_existing.clear()   # vacío → _check_* no filtra nada todavía

        for ele in self.manager.get_all_elements():
            if not isinstance(ele, (ForceBeamColumn, ForceBeamColumnHinge)):
                continue
            for sec_num in range(1, ele.integration_points + 1):
                sec_tag = self._get_section_tag(ele, sec_num)
                if sec_tag is None:
                    continue
                sec = self.manager.get_section(sec_tag)
                if sec is None:
                    continue
                temp = {"DL": None, "SL": None, "NC": None}
                if isinstance(sec, FiberSection):
                    self._check_fiber(ele, sec_num, sec, temp, 0.0)
                elif isinstance(sec, AggregatorSection):
                    self._check_aggregator(ele, sec_num, sec, temp, 0.0)
                for ls, val in temp.items():
                    if val is not None:
                        self._pre_existing.add((ele.tag, sec_num, ls))

        if self._pre_existing:
            print(f"[CodeLS] Pre-existentes por gravedad: {len(self._pre_existing)} sección-LS")

    def capture_step(self, roof_disp: float):
        for ele in self.manager.get_all_elements():
            if not isinstance(ele, (ForceBeamColumn, ForceBeamColumnHinge)):
                continue

            # Mapa rápido; fallback por geometría si el mapa no lo tiene
            y_level = self._elem_floor_map.get(ele.tag) or self._floor_from_node(ele)
            if y_level is None:
                continue

            floor_result = self._results.get(y_level)
            if floor_result is None:
                continue

            if all(v is not None for v in floor_result.values()):
                continue  # planta ya completa — no hay que revisar más

            for sec_num in range(1, ele.integration_points + 1):
                sec_tag = self._get_section_tag(ele, sec_num)
                if sec_tag is None:
                    continue
                sec = self.manager.get_section(sec_tag)
                if sec is None:
                    continue

                if isinstance(sec, FiberSection):
                    self._check_fiber(ele, sec_num, sec, floor_result, roof_disp)
                elif isinstance(sec, AggregatorSection):
                    self._check_aggregator(ele, sec_num, sec, floor_result, roof_disp)

    def get_results(self) -> dict:
        """{y_level: {"DL": float|None, "SL": float|None, "NC": float|None}}
        Sólo contiene valores distintos de None para LS activados durante el pushover
        por secciones que NO estaban pre-existentes bajo gravedad.
        """
        return {y: dict(ls_dict) for y, ls_dict in self._results.items()}

    # ─── Internos ─────────────────────────────────────────────────────────────

    def _floor_from_node(self, ele) -> float | None:
        """Fallback: deduce la planta del elemento por la coordenada Y de su nodo más alto."""
        ni = self.manager.get_node(ele.node_i)
        nj = self.manager.get_node(ele.node_j)
        if ni is None or nj is None:
            return None
        y_top = max(ni.y, nj.y)
        for y_floor in self._results:
            if abs(y_floor - y_top) < 1e-3:
                return y_floor
        return None

    def _build_maps(self):
        floor_data = self.manager.get_floor_data()
        if not floor_data:
            return
        base_y = min(floor_data.keys())
        for y, data in floor_data.items():
            if y <= base_y:
                continue
            self._results[y] = {"DL": None, "SL": None, "NC": None}
            for ele in data.get("columns", []):
                self._elem_floor_map[ele.tag] = y
            for ele in data.get("beams", []):
                self._elem_floor_map[ele.tag] = y

    def _get_section_tag(self, ele, sec_num: int):
        if isinstance(ele, ForceBeamColumn):
            return ele.section_tag
        if isinstance(ele, ForceBeamColumnHinge):
            if sec_num in (1, 2):
                return ele.section_i_tag
            if sec_num in (3, 4):
                return ele.section_e_tag
            if sec_num in (5, 6):
                return ele.section_j_tag
        return None

    def _fiber_mat_tags(self, fiber_sec: FiberSection) -> list:
        tags = []
        for p in fiber_sec.patches:
            tags.extend([p.material_tag] * (p.nIy * p.nIz))
        for layer in fiber_sec.layers:
            tags.extend([layer.material_tag] * layer.num_bars)
        return tags

    def _check_fiber(self, ele, sec_num: int, sec: FiberSection,
                     floor_result: dict, roof_disp: float):
        try:
            raw = ops.eleResponse(ele.tag, 'section', sec_num, 'fiberData')
        except Exception:
            return
        if not raw:
            return

        mat_tags = self._fiber_mat_tags(sec)
        n = min(len(raw) // 5, len(mat_tags))
        eps_sl = self.SL_FACTOR * self.EPSC_U
        eps_nc = self.NC_FACTOR * self.EPSC_U

        for i in range(n):
            strain = abs(raw[i * 5 + 4])
            mat = self.manager.get_material(mat_tags[i])
            if mat is None:
                continue

            if isinstance(mat, Steel01):
                eps_y = mat.get_yield_strain()
                if (eps_y and floor_result["DL"] is None and strain >= eps_y
                        and (ele.tag, sec_num, "DL") not in self._pre_existing):
                    floor_result["DL"] = roof_disp

            elif isinstance(mat, Concrete01):
                if (floor_result["SL"] is None and strain >= eps_sl
                        and (ele.tag, sec_num, "SL") not in self._pre_existing):
                    floor_result["SL"] = roof_disp
                if (floor_result["NC"] is None and strain >= eps_nc
                        and (ele.tag, sec_num, "NC") not in self._pre_existing):
                    floor_result["NC"] = roof_disp

    def _check_aggregator(self, ele, sec_num: int, sec: AggregatorSection,
                          floor_result: dict, roof_disp: float):
        try:
            deform = ops.eleResponse(ele.tag, 'section', sec_num, 'deformation')
        except Exception:
            return
        if not deform or len(deform) < 2:
            return

        kappa = abs(deform[1])

        for m_entry in sec.materials:
            if m_entry.get("dof") != "Mz":
                continue
            mat = self.manager.get_material(m_entry["mat_tag"])
            if mat is None:
                continue

            if floor_result["DL"] is None and (ele.tag, sec_num, "DL") not in self._pre_existing:
                v = mat.get_yield_strain()
                if v and kappa >= v:
                    floor_result["DL"] = roof_disp

            if floor_result["SL"] is None and (ele.tag, sec_num, "SL") not in self._pre_existing:
                v = mat.get_sl_strain()
                if v and kappa >= v:
                    floor_result["SL"] = roof_disp

            if floor_result["NC"] is None and (ele.tag, sec_num, "NC") not in self._pre_existing:
                v = mat.get_nc_strain()
                if v and kappa >= v:
                    floor_result["NC"] = roof_disp
