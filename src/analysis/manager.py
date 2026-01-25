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

        #Contador para los IDs automáticos
        self.next_material_tag = 1 
        self.next_section_tag = 1
        self.next_node_tag = 1
        self.next_element_tag = 1
        


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

        if node.tag >= self.next_node_tag:
            self.next_node_tag = node.tag + 1

    def get_node(self,tag):
        return self.node.get(tag)

    def delete_node(self,tag):
        if tag in self.node:
            del self.node[tag]
    
    def get_next_node_tag(self):
        return self.next_node_tag

    def get_all_nodes(self):
        return list(self.node.values())


## Elementos ## 
    def add_element(self, element):
        self.element[element.tag] = element

        if element.tag >= self.next_element_tag:
            self.next_element_tag = element.tag + 1

    def get_element(self,tag):
        return self.element.get(tag)

    def delete_element(self,tag):
        if tag in self.element:
            del self.element[tag]
   
    def get_next_element_tag(self):
        return self.next_element_tag

    def get_all_elements(self):
        return list(self.element.values())


## Guardar el projecto ##
    def save_project(self, filename):
        import json

        data ={
            "materials": [m.to_dict() for m in self.get_all_materials()],
            "sections": [s.to_dict() for s in self.get_all_sections()],
            "nodes": [n.to_dict() for n in self.get_all_nodes()],
            "elements": [e.to_dict() for e in self.get_all_elements()]
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

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            #Limpiar estado actual
            self.material = {}
            self.section = {}
            self.node = {}
            self.element = {}

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
            
            print(f"Projecto cargado: {len(self.node)} nodos, {len(self.element)} elementos")
            self.dataChanged.emit()
            return True

        except Exception as e:
            print(f"Error cargando projecto {e}")
            return False
