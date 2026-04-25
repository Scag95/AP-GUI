from PyQt6.QtCore import QObject, pyqtSignal

class ProjectManager(QObject):
    _instance = None
    dataChanged = pyqtSignal()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        #Un pequeño seguro: si ya está inicializado no hacemos nada
        if hasattr(self,"initialized"):
            return
        self.initialized = True
        
        #Base de datos. Guardamos el material.
        self.material = {}
        self.section = {}
        self.node = {}
        self.element = {}
        self.patterns = {}
        
        # Resultados de Análisis
        self.gravity_results = None
        self.pushover_results = None
        self.yield_history = []

        # Estados Límite (EC8)
        self.floor_limit_states: dict = {}
        self._ls_pre_existing: set   = set()
        self._ls_elem_floor_map: dict = {}

        # Almacén Cargas Temporales Pushover
        self.pushover_loads = []

        #Contador para los IDs automáticos
        self.next_material_tag = 1 
        self.next_section_tag = 1
        self.next_node_tag = 1
        self.next_element_tag = 1
        self.next_pattern_tag = 1

        #Caché de Topología (Pisos)
        self._topology_dirty = True
        self._floors_cache = {}        


 ## Materiales ##   
    def add_material(self,material):
        self.material[material.tag] = material

        if material.tag >= self.next_material_tag:
            self.next_material_tag = material.tag + 1

    def get_material(self,tag):
        return self.material.get(tag)

    def get_all_materials(self):
        return list(self.material.values())

    def delete_material(self,tag):
        if tag in self.material:
            del self.material[tag]

    def get_next_material_tag(self):
        return self.next_material_tag

## Secciones ##
    def add_section(self,section):
        self.section[section.tag] = section

        if section.tag >= self.next_section_tag:
            self.next_section_tag = section.tag + 1

    def get_section(self,tag):
        return self.section.get(tag)

    def get_all_sections(self):
        return list(self.section.values())

    def delete_section(self,tag):
        if tag in self.section:
            del self.section[tag]

    def get_next_section_tag(self):
        return self.next_section_tag

## Nodos ## 
    def add_node(self, node):
        self.node[node.tag] = node
        self.mark_topology_dirty()
        if node.tag >= self.next_node_tag:
            self.next_node_tag = node.tag + 1

    def get_node(self,tag):
        return self.node.get(tag)

    def delete_node(self,tag):
        self.mark_topology_dirty()
        if tag in self.node:
            del self.node[tag]
    
    def get_next_node_tag(self):
        return self.next_node_tag

    def get_all_nodes(self):
        return list(self.node.values())


## Elementos ## 
    def add_element(self, element):
        self.element[element.tag] = element
        self.mark_topology_dirty()

        if element.tag >= self.next_element_tag:
            self.next_element_tag = element.tag + 1

    def get_element(self,tag):
        return self.element.get(tag)

    def delete_element(self,tag):
        self.mark_topology_dirty()
        if tag in self.element:
            del self.element[tag]
   
    def get_next_element_tag(self):
        return self.next_element_tag

    def get_all_elements(self):
        return list(self.element.values())

## Pisos ##
    def get_floor_data(self):
        if not self._topology_dirty:
            return self._floors_cache

        floors = {}
        tolerance = 1e-3   # 1 mm de tolerancia
        
        #Agrupar nodos
        for node in self.get_all_nodes():
            y = node.y

            #buscar si el piso ya existe en nuestra tolerancia
            floor_y = None
            for key in floors.keys():
                if abs(key - y) < tolerance:
                    floor_y = key
                    break
            
            #Si no existe lo inicializamos
            if floor_y is None:
                floor_y = y
                floors[floor_y] = {"nodes": [], "columns": [], "beams": []}

            floors[floor_y]["nodes"].append(node)

        #Agrupar elementos

        for ele in self.get_all_elements():
            ni = self.get_node(ele.node_i)
            nj = self.get_node(ele.node_j)

            if not ni or not nj: continue

            #Diferencia principal (Vertical u Horizontal)
            dx = abs(nj.x - ni.x)
            dy = abs(nj.y - ni.y)
            
            is_column = dy > tolerance and dx < tolerance
            is_beam = dx > tolerance and dy < tolerance

            if is_column:
                #La columna pertence al piso de su nodo más alto.
                y_ceil = max(ni.y, nj.y)

                for floor_key in floors.keys():
                    if abs(floor_key - y_ceil) < tolerance:
                        floors[floor_key]["columns"].append(ele)
                        break

            elif is_beam:
                y_beam = ni.y

                for floor_key in floors.keys():
                    if abs(floor_key - y_beam) < tolerance:
                        floors[floor_key]["beams"].append(ele)
                        break

        #Guardamos en caché el diccionario ordenado
        self._floors_cache = dict(sorted(floors.items()))
        self._topology_dirty = False

        return self._floors_cache

    def mark_topology_dirty(self):
        """Avisa al manager que las coordenadas o elementos han cambiado"""
        self._topology_dirty = True
        self.gravity_results = None
        self.pushover_results = None

## Masas ##
    def get_floor_masses(self):
        """Calcula las masas concentradas horizontal para cada planta"""
        floor_masses = {}
        floor_data = self.get_floor_data()

        #1. Obtener la lista ordenadas de alturas Y
        sorted_ys = list(floor_data.keys())

        #2. Iterrar por cada piso para rellenar las masas
        for i, y_floor in enumerate(sorted_ys):
            total_mass_x = 0.0
            elements_dict = floor_data[y_floor]

            # Masas nodales concentradas
            for node in elements_dict.get("nodes", []):
                if node.mass is not None and len(node.mass) > 0:
                    # Asumiendo que buscamos la masa efectiva en la dirección X
                    total_mass_x += node.mass[0]

            # Masa de las vigas
            for beam in elements_dict.get("beams",[]):
                ni = self.get_node(beam.node_i)
                nj = self.get_node(beam.node_j)
                if not ni or not nj: continue

                L = ((nj.x - ni.x)**2 + (nj.y - ni.y)**2)**0.5
                rho = getattr(beam, 'mass_density')
                total_mass_x += (L * rho)

            #Masa de las columnas
            for col in elements_dict.get("columns", []):
                ni = self.get_node(col.node_i)
                nj = self.get_node(col.node_j)
                if not ni or not nj: continue

                l_col = abs(nj.y - ni.y)
                rho_col = getattr(col, 'mass_density')
                mass_col = l_col * rho_col

                #mitad para el piso actual
                total_mass_x += (mass_col/2.0)

                if i > 0:
                    y_prev = sorted_ys[i-1]

                    is_base = False
                    for node in floor_data[y_prev]["nodes"]:
                        if node.fixity[0] == 1 or node.fixity[1] == 1:
                            is_base = True
                            break
                    
                    if not is_base:
                        if y_prev not in floor_masses: 
                            floor_masses[y_prev] = 0.0
                        floor_masses[y_prev] += (mass_col/2.0)

            #Guardamos la masa calcula hasta ahora para este y_floor
            if y_floor not in floor_masses:
                floor_masses[y_floor] = 0.0
            floor_masses[y_floor] += total_mass_x
            
        return floor_masses

## Patrones de Carga ##
    def add_pattern(self, pattern):
        self.patterns[pattern.tag] = pattern
        if pattern.tag >= self.next_pattern_tag:
            self.next_pattern_tag = pattern.tag + 1
        self.gravity_results = None
        self.pushover_results = None
        self.dataChanged.emit()

    def get_pattern(self, tag):
        return self.patterns.get(tag)

    def get_all_patterns(self):
        return list(self.patterns.values())

    def delete_pattern(self, tag):
        if tag in self.patterns:
            del self.patterns[tag]
            self.gravity_results = None
            self.pushover_results = None
            self.dataChanged.emit()

    def get_next_pattern_tag(self):
        return self.next_pattern_tag

## Cargas (Loads) anidadas ##
    def add_load(self, load, pattern_tag: int = 1):
        # Insertar carga en su respectiva carpeta
        pattern = self.get_pattern(pattern_tag)
        if not pattern:
            print(f"Error: No existe el patrón {pattern_tag}")
            return
        if load.tag == 0:
            load.tag = self.get_next_load_tag()
        pattern.add_load(load)
        self.gravity_results = None
        self.pushover_results = None
        self.dataChanged.emit()

    def get_load(self, tag):
        for p in self.patterns.values():
            for l in p.loads:
                if l.tag == tag:
                    return l
        return None

    def delete_load(self, tag):
        for p in self.patterns.values():
            p.remove_load(tag)
        self.gravity_results = None
        self.pushover_results = None
        self.dataChanged.emit()

    def get_next_load_tag(self):
        loads = self.get_all_loads()
        if not loads: return 1
        return max(l.tag for l in loads) + 1

    def get_all_loads(self):
        loads = []
        for p in self.patterns.values():
            loads.extend(p.loads)
        return loads



## Guardar el projecto ##
    def save_project(self, filename):
        import json

        data ={
            "materials": [m.to_dict() for m in self.get_all_materials()],
            "sections": [s.to_dict() for s in self.get_all_sections()],
            "nodes": [n.to_dict() for n in self.get_all_nodes()],
            "elements": [e.to_dict() for e in self.get_all_elements()],
            "patterns": [p.to_dict() for p in self.get_all_patterns()]
        }

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent = 4)
            print(f"Proyecto guardado exitosamente en: {filename}")
            return True
        except Exception as e:
            print(f"Error guardando proyecto: {e}")
            return False

    def load_project(self,filename):
        import json
        from src.analysis.materials import Concrete01, Steel01, Hysteretic, HystereticSM
        from src.analysis.sections import FiberSection, AggregatorSection
        from src.analysis.node import Node
        from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
        from src.analysis.loads import NodalLoad, ElementLoad, LoadPattern   

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            #Limpieza de datos antiguos
            self.new_project() 
            #1. Cargar Materiales
            for m_data in data.get("materials",[]):
                tipo = m_data.get("type")
                if tipo == "Concrete01":
                    mat = Concrete01.from_dict(m_data)
                elif tipo == "Steel01":
                    mat = Steel01.from_dict(m_data)
                elif tipo == "Hysteretic":
                    mat = Hysteretic.from_dict(m_data)
                elif tipo == "HystereticSM":
                    mat = HystereticSM.from_dict(m_data)
                elif tipo == "Elastic":
                    from src.analysis.materials import Elastic
                    mat = Elastic.from_dict(m_data)
                else:
                    continue
                self.add_material(mat)

            #2. Cargar secciones
            for s_data in data.get("sections",[]):
                tipo = s_data.get("type")
                if tipo == "FiberSection":
                    sec = FiberSection.from_dict(s_data)
                    self.add_section(sec)
                elif tipo == "AggregatorSection":
                    sec = AggregatorSection.from_dict(s_data)
                    self.add_section(sec)
            
            #3. Cargar Nodos
            for n_data in data.get("nodes",[]):
                node = Node.from_dict(n_data)
                self.add_node(node)

            #4. Cargar Elementos
            for e_data in data.get("elements", []):
                if e_data.get("type") == "ForceBeamColumn":
                    element = ForceBeamColumn.from_dict(e_data)
                    self.add_element(element)
                elif e_data.get("type") == "ForceBeamColumnHinge":
                    element = ForceBeamColumnHinge.from_dict(e_data)
                    self.add_element(element)
            
            # 5. Cargar Patrones de Carga
            for p_data in data.get("patterns", []):
                pattern = LoadPattern.from_dict(p_data)
                self.add_pattern(pattern)

            self.mark_topology_dirty()

            print(f"Projecto cargado: {len(self.node)} nodos, {len(self.element)} elementos")
            self.dataChanged.emit()
            return True

        except Exception as e:
            print(f"Error cargando projecto {e}")
            return False
    
    def new_project(self):
        """Reinicia completamente el estado del proyecto."""
        # Limpiar diccionarios
        self.material.clear()
        self.section.clear()
        self.node.clear()
        self.element.clear()
        self.patterns.clear()
        
        # Limpiar resultados y temporales
        self.gravity_results = None
        self.pushover_results = None
        self.yield_history = []
        self.floor_limit_states.clear()
        self._ls_pre_existing.clear()
        self._ls_elem_floor_map.clear()
        self.pushover_loads.clear()
        
        # Reiniciar contadores
        self.next_material_tag = 1
        self.next_section_tag = 1
        self.next_node_tag = 1
        self.next_element_tag = 1
        self.next_pattern_tag = 1
        
        # Notificar a la UI que todo cambió (se borró)
        self.dataChanged.emit()

## Detección de Estados Límite (EC8) ##

    EPSC_U    = 0.0035
    SL_FACTOR = 0.75
    NC_FACTOR = 1.25
    _LS_RANK  = {"DL": 1, "SL": 2, "NC": 3}

    # ── API pública ───────────────────────────────────────────────────────────

    def reset_limit_states(self):
        """Reinicia mapas internos. Llamar antes de cada análisis o ronda."""
        self.floor_limit_states.clear()
        self._ls_pre_existing.clear()
        self._ls_elem_floor_map.clear()
        self._ls_build_floor_map()

    def capture_limit_state_baseline(self):
        """Registra estados ya activos bajo gravedad para filtrarlos durante el pushover."""
        from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
        from src.analysis.sections import FiberSection, AggregatorSection

        self._ls_pre_existing.clear()
        for ele in self.get_all_elements():
            if not isinstance(ele, (ForceBeamColumn, ForceBeamColumnHinge)):
                continue
            for sec_num in range(1, ele.integration_points + 1):
                sec_tag = self._ls_get_sec_tag(ele, sec_num)
                if sec_tag is None:
                    continue
                sec = self.get_section(sec_tag)
                if sec is None:
                    continue
                temp = {"DL": None, "SL": None, "NC": None}
                if isinstance(sec, FiberSection):
                    self._ls_check_fiber(ele, sec_num, sec, temp, 0.0)
                elif isinstance(sec, AggregatorSection):
                    self._ls_check_aggregator(ele, sec_num, sec, temp, 0.0)
                for ls, val in temp.items():
                    if val is not None:
                        self._ls_pre_existing.add((ele.tag, sec_num, ls))

        if self._ls_pre_existing:
            print(f"[LimitState] Pre-existentes bajo gravedad: {len(self._ls_pre_existing)}")

    def capture_limit_state_step(self, roof_disp: float):
        """
        Llamar una vez por paso del pushover.
        Actualiza yield_history (visualización) y floor_limit_states (curva).
        """
        from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
        from src.analysis.sections import FiberSection, AggregatorSection

        step_yield = {}

        for ele in self.get_all_elements():
            if not isinstance(ele, (ForceBeamColumn, ForceBeamColumnHinge)):
                continue

            y_level  = self._ls_elem_floor_map.get(ele.tag) or self._ls_floor_from_node(ele)
            floor_rs = self.floor_limit_states.get(y_level)
            floor_ok = floor_rs is None or all(v is not None for v in floor_rs.values())

            ele_yield = {}
            for sec_num in range(1, ele.integration_points + 1):
                sec_tag = self._ls_get_sec_tag(ele, sec_num)
                if sec_tag is None:
                    continue
                sec = self.get_section(sec_tag)
                if sec is None:
                    continue

                if isinstance(sec, FiberSection):
                    y_data = self._ls_yield_fiber(ele, sec_num, sec)
                    if y_data:
                        ele_yield[sec_num] = y_data
                    if floor_rs and not floor_ok:
                        self._ls_check_fiber(ele, sec_num, sec, floor_rs, roof_disp)

                elif isinstance(sec, AggregatorSection):
                    y_data = self._ls_yield_aggregator(ele, sec_num, sec)
                    if y_data:
                        ele_yield[sec_num] = y_data
                    if floor_rs and not floor_ok:
                        self._ls_check_aggregator(ele, sec_num, sec, floor_rs, roof_disp)

            if ele_yield:
                step_yield[ele.tag] = ele_yield

        self.yield_history.append(step_yield)

    def get_floor_limit_states(self) -> dict:
        return {y: dict(d) for y, d in self.floor_limit_states.items()}

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _ls_build_floor_map(self):
        floor_data = self.get_floor_data()
        if not floor_data:
            return
        base_y = min(floor_data.keys())
        for y, data in floor_data.items():
            if y <= base_y:
                continue
            self.floor_limit_states[y] = {"DL": None, "SL": None, "NC": None}
            for ele in data.get("columns", []):
                self._ls_elem_floor_map[ele.tag] = y
            for ele in data.get("beams", []):
                self._ls_elem_floor_map[ele.tag] = y

    def _ls_floor_from_node(self, ele):
        ni = self.get_node(ele.node_i)
        nj = self.get_node(ele.node_j)
        if not ni or not nj:
            return None
        y_top = max(ni.y, nj.y)
        for y in self.floor_limit_states:
            if abs(y - y_top) < 1e-3:
                return y
        return None

    def _ls_get_sec_tag(self, ele, sec_num: int):
        from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
        if isinstance(ele, ForceBeamColumn):
            return ele.section_tag
        if isinstance(ele, ForceBeamColumnHinge):
            if sec_num in (1, 2): return ele.section_i_tag
            if sec_num in (3, 4): return ele.section_e_tag
            if sec_num in (5, 6): return ele.section_j_tag
        return None

    def _ls_get_loc(self, ele, sec_num: int) -> float:
        import openseespy.opensees as ops
        try:
            return ops.sectionLocation(ele.tag, sec_num)
        except Exception:
            return (sec_num - 1) / max(ele.integration_points - 1, 1)

    def _ls_fiber_mat_tags(self, fiber_sec) -> list:
        tags = []
        for p in fiber_sec.patches:
            tags.extend([p.material_tag] * (p.nIy * p.nIz))
        for layer in fiber_sec.layers:
            tags.extend([layer.material_tag] * layer.num_bars)
        return tags

    def _ls_get_mz_mat(self, sec):
        from src.analysis.sections import AggregatorSection
        if not isinstance(sec, AggregatorSection):
            return None
        for m in sec.materials:
            if m['dof'] == 'Mz':
                return self.get_material(m['mat_tag'])
        return None

    def _ls_yield_fiber(self, ele, sec_num: int, fiber_sec):
        import openseespy.opensees as ops
        try:
            raw = ops.eleResponse(ele.tag, 'section', sec_num, 'fiberData')
        except Exception:
            return None
        if not raw:
            return None

        mat_tags  = self._ls_fiber_mat_tags(fiber_sec)
        max_ratio = 0.0
        max_strain = 0.0
        for i in range(min(len(raw) // 5, len(mat_tags))):
            strain = raw[i * 5 + 4]
            mat    = self.get_material(mat_tags[i])
            eps_y  = mat.get_yield_strain() if mat else None
            if not eps_y or eps_y <= 0:
                continue
            ratio = abs(strain) / eps_y
            if ratio > max_ratio:
                max_ratio, max_strain = ratio, strain

        if max_ratio > 0:
            return {"ratio": max_ratio, "strain": max_strain,
                    "loc": self._ls_get_loc(ele, sec_num), "limit_state": "DL"}
        return None

    def _ls_yield_aggregator(self, ele, sec_num: int, sec):
        import openseespy.opensees as ops
        try:
            deform = ops.eleResponse(ele.tag, 'section', sec_num, 'deformation')
        except Exception:
            return None
        if not deform or len(deform) < 2:
            return None

        raw_kappa = deform[1]
        sign  = 1 if raw_kappa >= 0 else -1
        kappa = abs(raw_kappa)
        mat   = self._ls_get_mz_mat(sec)
        if mat is None:
            return None

        kappa_y = mat.get_yield_strain(sign)
        if not kappa_y or kappa_y <= 0:
            return None

        ratio = kappa / kappa_y
        if ratio > 0:
            ls     = "DL"
            sl_val = mat.get_sl_strain(sign)
            nc_val = mat.get_nc_strain(sign)
            if nc_val and kappa >= nc_val:
                ls = "NC"
            elif sl_val and kappa >= sl_val:
                ls = "SL"
            return {"ratio": ratio, "strain": raw_kappa,
                    "loc": self._ls_get_loc(ele, sec_num), "limit_state": ls}
        return None

    def _ls_check_fiber(self, ele, sec_num: int, sec, floor_result: dict, roof_disp: float):
        import openseespy.opensees as ops
        from src.analysis.materials import Steel01, Concrete01
        try:
            raw = ops.eleResponse(ele.tag, 'section', sec_num, 'fiberData')
        except Exception:
            return
        if not raw:
            return

        mat_tags = self._ls_fiber_mat_tags(sec)
        n        = min(len(raw) // 5, len(mat_tags))
        eps_sl   = self.SL_FACTOR * self.EPSC_U
        eps_nc   = self.NC_FACTOR * self.EPSC_U

        for i in range(n):
            strain = abs(raw[i * 5 + 4])
            mat    = self.get_material(mat_tags[i])
            if mat is None:
                continue
            if isinstance(mat, Steel01):
                eps_y = mat.get_yield_strain()
                if (eps_y and floor_result["DL"] is None and strain >= eps_y
                        and (ele.tag, sec_num, "DL") not in self._ls_pre_existing):
                    floor_result["DL"] = roof_disp
            elif isinstance(mat, Concrete01):
                if (floor_result["SL"] is None and strain >= eps_sl
                        and (ele.tag, sec_num, "SL") not in self._ls_pre_existing):
                    floor_result["SL"] = roof_disp
                if (floor_result["NC"] is None and strain >= eps_nc
                        and (ele.tag, sec_num, "NC") not in self._ls_pre_existing):
                    floor_result["NC"] = roof_disp

    def _ls_check_aggregator(self, ele, sec_num: int, sec, floor_result: dict, roof_disp: float):
        import openseespy.opensees as ops
        try:
            deform = ops.eleResponse(ele.tag, 'section', sec_num, 'deformation')
        except Exception:
            return
        if not deform or len(deform) < 2:
            return

        raw_kappa = deform[1]
        sign  = 1 if raw_kappa >= 0 else -1
        kappa = abs(raw_kappa)
        mat   = self._ls_get_mz_mat(sec)
        if mat is None:
            return

        if floor_result["DL"] is None and (ele.tag, sec_num, "DL") not in self._ls_pre_existing:
            v = mat.get_yield_strain(sign)
            if v and kappa >= v:
                floor_result["DL"] = roof_disp
        if floor_result["SL"] is None and (ele.tag, sec_num, "SL") not in self._ls_pre_existing:
            v = mat.get_sl_strain(sign)
            if v and kappa >= v:
                floor_result["SL"] = roof_disp
        if floor_result["NC"] is None and (ele.tag, sec_num, "NC") not in self._ls_pre_existing:
            v = mat.get_nc_strain(sign)
            if v and kappa >= v:
                floor_result["NC"] = roof_disp