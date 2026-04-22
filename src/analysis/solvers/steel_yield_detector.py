import openseespy.opensees as ops
from src.analysis.manager import ProjectManager
from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
from src.analysis.sections import FiberSection, AggregatorSection


class SteelYieldDetector:

    _LS_RANK = {"DL": 1, "SL": 2, "NC": 3}

    def __init__(self):
        self.manager = ProjectManager.instance()
        self._baseline: dict = {}   # {(ele_tag, sec_num): "DL"|"SL"|"NC"}

    def reset(self):
        self._baseline.clear()

    def capture_baseline(self):
        """
        Registra el LS de cada sección fluida bajo gravedad.
        En capture_step, esas secciones solo aparecen si progresan a un LS mayor.
        """
        self._baseline.clear()
        raw = self._capture_raw()
        for ele_tag, sections in raw.items():
            for sec_num, data in sections.items():
                if data.get("ratio", 0.0) >= 1.0:
                    self._baseline[(ele_tag, sec_num)] = data.get("limit_state", "DL")
        if self._baseline:
            print(f"[YieldDetector] Baseline gravedad: {len(self._baseline)} secciones pre-fluidas")

    # ─── Helpers comunes ──────────────────────────────────────────────────────

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

    def _get_loc(self, ele, sec_num: int) -> float:
        try:
            return ops.sectionLocation(ele.tag, sec_num)
        except Exception:
            return (sec_num - 1) / max(ele.integration_points - 1, 1)

    # ─── Path A: FiberSection — usa fiberData ─────────────────────────────────

    def _get_fiber_material_tags(self, fiber_sec: FiberSection) -> list:
        """Lista de mat_tag en el mismo orden que OpenSees define las fibras."""
        tags = []
        for p in fiber_sec.patches:
            tags.extend([p.material_tag] * (p.nIy * p.nIz))
        for layer in fiber_sec.layers:
            tags.extend([layer.material_tag] * layer.num_bars)
        return tags

    def _capture_fiber_section(self, ele, sec_num: int, fiber_sec: FiberSection):
        try:
            raw = ops.eleResponse(ele.tag, 'section', sec_num, 'fiberData')
        except Exception:
            return None

        if not raw:
            return None

        mat_tags = self._get_fiber_material_tags(fiber_sec)
        n_fibers = len(raw) // 5

        max_ratio  = 0.0
        max_strain = 0.0

        for i in range(min(n_fibers, len(mat_tags))):
            strain  = raw[i * 5 + 4]
            mat     = self.manager.get_material(mat_tags[i])
            eps_y   = mat.get_yield_strain() if mat else None
            if eps_y is None or eps_y <= 0:
                continue
            ratio = abs(strain) / eps_y
            if ratio > max_ratio:
                max_ratio  = ratio
                max_strain = strain

        if max_ratio > 0:
            return {
                "ratio":       max_ratio,
                "strain":      max_strain,
                "loc":         self._get_loc(ele, sec_num),
                "limit_state": "DL"   # FiberSection solo rastrea fluencia de acero
            }
        return None

    # ─── Path B: AggregatorSection — usa deformation + κ ─────────────────────

    def _get_mz_material(self, sec_tag: int):
        sec = self.manager.get_section(sec_tag)
        if not isinstance(sec, AggregatorSection):
            return None
        for m in sec.materials:
            if m['dof'] == 'Mz':
                return self.manager.get_material(m['mat_tag'])
        return None

    def _capture_aggregator_section(self, ele, sec_num: int, sec_tag: int):
        try:
            deformation = ops.eleResponse(ele.tag, 'section', sec_num, 'deformation')
        except Exception:
            return None

        if not deformation or len(deformation) < 2:
            return None

        kappa = deformation[1]
        mat   = self._get_mz_material(sec_tag)
        if mat is None:
            return None

        kappa_y = mat.get_yield_strain()
        if kappa_y is None or kappa_y <= 0:
            return None

        ratio = abs(kappa) / kappa_y
        if ratio > 0:
            kappa_abs = abs(kappa)
            ls = "DL"
            sl_val = mat.get_sl_strain()
            nc_val = mat.get_nc_strain()
            if nc_val and kappa_abs >= nc_val:
                ls = "NC"
            elif sl_val and kappa_abs >= sl_val:
                ls = "SL"

            return {
                "ratio":       ratio,
                "strain":      kappa,
                "loc":         self._get_loc(ele, sec_num),
                "limit_state": ls
            }
        return None

    # ─── Captura principal ────────────────────────────────────────────────────

    def _capture_raw(self) -> dict:
        """Captura sin filtrar: {ele_tag: {sec_num: {ratio, strain, loc}}}."""
        step_data = {}

        for ele in self.manager.get_all_elements():
            if not isinstance(ele, (ForceBeamColumn, ForceBeamColumnHinge)):
                continue

            ele_data = {}

            for sec_num in range(1, ele.integration_points + 1):
                sec_tag = self._get_section_tag(ele, sec_num)
                if sec_tag is None:
                    continue

                sec = self.manager.get_section(sec_tag)
                if sec is None:
                    continue

                if isinstance(sec, FiberSection):
                    result = self._capture_fiber_section(ele, sec_num, sec)
                elif isinstance(sec, AggregatorSection):
                    result = self._capture_aggregator_section(ele, sec_num, sec_tag)
                else:
                    continue

                if result:
                    ele_data[sec_num] = result

            if ele_data:
                step_data[ele.tag] = ele_data

        return step_data

    def capture_step(self) -> dict:
        """
        {ele_tag: {sec_num: {ratio, strain, loc, limit_state}}} — ratio >= 1 indica fluencia.
        Secciones pre-existentes (baseline) solo aparecen si han progresado a un LS mayor.
        """
        raw = self._capture_raw()
        if not self._baseline:
            return raw

        filtered = {}
        for ele_tag, sections in raw.items():
            kept = {}
            for sec_num, data in sections.items():
                baseline_ls = self._baseline.get((ele_tag, sec_num))
                if baseline_ls is None:
                    # No estaba en baseline: mostrar si ha fluido
                    if data.get("ratio", 0.0) >= 1.0:
                        kept[sec_num] = data
                else:
                    # Estaba en baseline: mostrar solo si ha progresado a LS mayor
                    current_rank  = self._LS_RANK.get(data.get("limit_state", "DL"), 1)
                    baseline_rank = self._LS_RANK.get(baseline_ls, 1)
                    if current_rank > baseline_rank:
                        kept[sec_num] = data
            if kept:
                filtered[ele_tag] = kept
        return filtered
