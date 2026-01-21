class ProjectManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        #Un pequeño seguro: si ya está inicializado no hacemos nada
        if hasattr(self,"initialized"):
            return
        self.initialized = True
        
        #Base de datos. Guardamos el material.
        self.material = {}
        self.section = {}

        #Contador para los IDs automáticos
        self.next_material_tag = 1 
        self.next_section_tag = 1


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
        