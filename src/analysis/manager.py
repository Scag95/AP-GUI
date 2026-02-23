from PyQt6.QtCore import QObject, pyqtSignal
import math

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
        self.load = {}
        
        # Resultados de Análisis
        self.gravity_results = None
        self.pushover_results = None

        #Contador para los IDs automáticos
        self.next_material_tag = 1 
        self.next_section_tag = 1
        self.next_node_tag = 1
        self.next_element_tag = 1
        self.next_load_tag = 1

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

                #Buscar el piso correspondiente
                for key in floors.keys():
                    if abs(key - y_ceil) < tolerance:
                        floors[key]["columns"].append(ele)
                        break

                    elif is_beam:
                        y_beam = ni.y

                        for key in floors.keys():
                            if abs(key-y_beam) < tolerance:
                                floors[key]["beams"].append(ele)
                                break

            #Gurdamos en caché el diccionario ordenado
            self._floors_cache = dict(sorted(floors.items()))
            self._topology_dirty = False

        return self._floors_cache

    def mark_topology_dirty(self):
        """Avisa al manager que las coordenadas o elementos han cambiado"""
        self._topology_dirty = True

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

## Cargas (Loads) ##
    def add_load(self, load):
        if load.tag == 0:
            load.tag = self.next_load_tag
        self.load[load.tag] = load
        if load.tag >= self.next_load_tag:
            self.next_load_tag = load.tag + 1
        self.dataChanged.emit()
    def get_load(self, tag):
        return self.load.get(tag)
    def delete_load(self, tag):
        if tag in self.load:
            del self.load[tag]
            self.dataChanged.emit()
    def get_next_load_tag(self):
        return self.next_load_tag
    def get_all_loads(self):
        return list(self.load.values())



## Guardar el projecto ##
    def save_project(self, filename):
        import json

        data ={
            "materials": [m.to_dict() for m in self.get_all_materials()],
            "sections": [s.to_dict() for s in self.get_all_sections()],
            "nodes": [n.to_dict() for n in self.get_all_nodes()],
            "elements": [e.to_dict() for e in self.get_all_elements()],
            "loads": [l.to_dict() for l in self.get_all_loads()]
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
        from src.analysis.materials import Concrete01, Steel01
        from src.analysis.sections import FiberSection
        from src.analysis.node import Node
        from src.analysis.element import ForceBeamColumn
        from src.analysis.loads import NodalLoad, ElementLoad   

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
                else:
                    continue
                self.add_material(mat)

            #2. Cargar secciones
            for s_data in data.get("sections",[]):
                if s_data.get("type") == "FiberSection":
                    sec = FiberSection.from_dict(s_data)
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
            
            # 5. Cargar Cargas (Loads)
            for l_data in data.get("loads", []):
                tipo = l_data.get("type")
                if tipo == "NodalLoad":
                    load = NodalLoad.from_dict(l_data)
                elif tipo == "ElementLoad":
                    load = ElementLoad.from_dict(l_data)
                else:
                    continue
                self.add_load(load)
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
        self.element.clear()
        self.load.clear()
        
        # Limpiar resultados
        self.gravity_results = None
        self.pushover_results = None
        # Reiniciar contadores
        self.next_material_tag = 1
        self.next_section_tag = 1
        self.next_node_tag = 1
        self.next_element_tag = 1
        self.next_load_tag = 1
        
        # Notificar a la UI que todo cambió (se borró)
        self.dataChanged.emit()