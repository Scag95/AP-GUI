from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QLabel, QDoubleSpinBox, QSpinBox, QComboBox, QPushButton, QHBoxLayout, QFormLayout
)
from PyQt6.QtCore import Qt
from src.analysis.manager import ProjectManager
from src.analysis.node import Node
from src.analysis.element import ForceBeamColumn
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitType



class GeometryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir Nodos y Elementos")
        self.resize(400,300)

        self.manager = ProjectManager.instance()

        #Crear el layout principal del QDialog
        self.main_layout = QVBoxLayout(self)

        #Creación del contenedor de pestañas
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        #Creación de las (páginas) para cada pestaña

        self.tab_nodes = QWidget()
        self.tab_elements = QWidget()

        #Añadimos las paginas al contenerdor principal
        self.tabs.addTab(self.tab_nodes, "Nodos")
        self.tabs.addTab(self.tab_elements, "Elementos")

        #Llamar a los métodos contructores del diseño interno
        self.setup_nodes_tab()
        self.setup_elements_tab()
        self.tabs.currentChanged.connect(self.on_tab_changed)



    def setup_nodes_tab(self):
        """ Configura la interfaz de la pestaña de Nodos """

        # Usamos QHBoxLayout para partir la pantalla en Izquierda/Derecha
        main_h_layout = QHBoxLayout(self.tab_nodes)
        
        # --- 1. Panel Izquierdo ---
        self.list_nodes = QListWidget()
        main_h_layout.addWidget(self.list_nodes, stretch=1)
        
        # --- 2. Panel Derecho ---
        right_panel = QVBoxLayout()
        form_layout = QFormLayout()

        #Creamos el input para el usuario
        self.spin_x = UnitSpinBox(UnitType.LENGTH)
        self.spin_x.setRange(-999999.0, 999999.0)
        self.spin_x.setDecimals(4)

        self.spin_y = UnitSpinBox(UnitType.LENGTH)
        self.spin_y.setRange(-999999.0, 999999.0)
        self.spin_y.setDecimals(4)
        
        #Añadimos las filas al formulario
        form_layout.addRow("Coordenada X:", self.spin_x)
        form_layout.addRow("Coordenada Y:", self.spin_y)
       
        right_panel.addLayout(form_layout)

        # Botones de acción
        self.btn_add_node = QPushButton("Añadir Nodo")
        self.btn_mod_node = QPushButton("Modificar Nodo")
        self.btn_del_node = QPushButton("Borrar Nodo")
        
        right_panel.addWidget(self.btn_add_node)
        right_panel.addWidget(self.btn_mod_node)
        right_panel.addWidget(self.btn_del_node)
        right_panel.addStretch()

        #Añadimos la cilumna de la dertecha entrera al layout principal
        main_h_layout.addLayout(right_panel, stretch=2)

        #Conectamos el boton a la función
        self.btn_add_node.clicked.connect(self.on_add_node_clicked)
        self.btn_del_node.clicked.connect(self.delete_node)
        self.btn_mod_node.clicked.connect(self.update_node)
        self.list_nodes.itemClicked.connect(self.on_node_selected)

        #Llenamos la lista por si el proyecto ya tenía nodos creados
        self.refresh_node_list()

    def on_add_node_clicked(self):
        """ Controla el evento de creación de nodo """

        #Obtenemos los valores del usuario
        x_val = self.spin_x.get_value_base()
        y_val = self.spin_y.get_value_base()


        # Le pedimos al Manager el siguiente tag del nodo
        manager = ProjectManager.instance()
        next_tag = manager.get_next_node_tag()

        #Creamos el nodo 
        new_node = Node(next_tag, x_val, y_val)

        #Se lo pasamos al manager para que lo almacene
        manager.add_node(new_node)
        manager.dataChanged.emit()

        #Limpiamos los spinbox
        self.spin_x.set_value_base(0.0)
        self.spin_y.set_value_base(0.0)
        self.spin_x.setFocus()

    def refresh_node_list(self):
        """ Función auxiliar que limpia la lista y vuelve a cargar todos los nodos creados """
        self.list_nodes.clear()
        manager = ProjectManager.instance()
        for node in manager.get_all_nodes():
            display_text = f"Nodo {node.tag}: (X: {node.x:.3f}, Y: {node.y:.3f})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, node.tag)
            self.list_nodes.addItem(item)

    def on_node_selected(self, item):
        tag = item.data(Qt.ItemDataRole.UserRole)
        manager = ProjectManager.instance()
        node = manager.get_node(tag)
        if node:
            self.spin_x.set_value_base(node.x)
            self.spin_y.set_value_base(node.y)

    def delete_node(self):
        current_row = self.list_nodes.currentRow()
        if current_row < 0: return

        item = self.list_nodes.item(current_row)
        tag_to_delete = item.data(Qt.ItemDataRole.UserRole)

        manager = ProjectManager.instance()
        manager.delete_node(tag_to_delete)
        manager.dataChanged.emit()
        self.refresh_node_list()

    def update_node(self):
        current_row = self.list_nodes.currentRow()
        if current_row < 0: return 

        item = self.list_nodes.item(current_row)
        tag_to_modify = item.data(Qt.ItemDataRole.UserRole)

        manager = ProjectManager.instance()
        node = manager.get_node(tag_to_modify)

        if node:
            node.x = self.spin_x.get_value_base()
            node.y = self.spin_y.get_value_base()
            manager.dataChanged.emit()
            self.refresh_node_list()
            
            # Restaurar la selección
            for i in range(self.list_nodes.count()):
                list_item = self.list_nodes.item(i)
                if list_item.data(Qt.ItemDataRole.UserRole) == tag_to_modify:
                    self.list_nodes.setCurrentItem(list_item)
                    break

    def setup_elements_tab(self):
        """ Configura la interfaz de la pestaña de los elementos """
        
        main_h_layout = QHBoxLayout(self.tab_elements)
        
        # --- 1. Panel Izquierdo ---
        self.list_elements = QListWidget()
        main_h_layout.addWidget(self.list_elements, stretch=1)
        
        # --- 2. Panel Derecho ---
        right_panel = QVBoxLayout()
        form_layout = QFormLayout()

        #Comboboxes para quee lusuaurio selecciones los recursos existentes

        self.cb_node_i = QComboBox()
        self.cb_node_j = QComboBox()
        self.cb_section = QComboBox()

        # Spinbox para los parámetros de análisis de Opensees
        self.spin_transf = QSpinBox()
        self.spin_transf.setRange(1,999)
        self.spin_transf.setValue(1)
        
        self.spin_int_pts = QSpinBox()
        self.spin_int_pts.setRange(1,10)
        self.spin_int_pts.setValue(5)

        form_layout.addRow("Nodo Inicial", self.cb_node_i)
        form_layout.addRow("Nodo Final", self.cb_node_j)
        form_layout.addRow("Sección Transversal", self.cb_section)
        form_layout.addRow("Tag Transformación Geometríca", self.spin_transf)
        form_layout.addRow("Puntos de Integración", self.spin_int_pts)

        right_panel.addLayout(form_layout)

        # Botones
        self.btn_add_element = QPushButton("Añadir Elemento")
        self.btn_mod_element = QPushButton("Modificar Elemento")
        self.btn_del_element = QPushButton("Borrar Elemento")
        
        right_panel.addWidget(self.btn_add_element)
        right_panel.addWidget(self.btn_mod_element)
        right_panel.addWidget(self.btn_del_element)
        right_panel.addStretch()
        
        main_h_layout.addLayout(right_panel, stretch=2)

        #Conectar el boton a la función de guardado

        self.btn_add_element.clicked.connect(self.on_add_element_clicked)
        self.btn_del_element.clicked.connect(self.delete_element)
        self.btn_mod_element.clicked.connect(self.update_element)
        self.list_elements.itemClicked.connect(self.on_element_selected)

        #En el momento que se dibuja el layout, cargamos listas
        self.load_data()

    def load_data(self):
        """ Llena los comboboxes leyendo los datos del ProjectManager """
        #Limpiar po si se llama múltiples veces
        self.cb_node_i.clear()
        self.cb_node_j.clear()
        self.cb_section.clear()
        self.list_elements.clear() 

        manager = ProjectManager.instance()
        
        #Leer los nodos existentes y cargar los combos

        for node in manager.get_all_nodes():
            display_text = f"Nodo {node.tag} (x:{node.x:.2f}, y:{node.y:.2f})"
            self.cb_node_i.addItem(display_text, node.tag)
            self.cb_node_j.addItem(display_text, node.tag)

        #Leer secciones existentes
        for sec in manager.get_all_sections():
            display_text = f"Sección {sec.tag} - {sec.name}"
            self.cb_section.addItem(display_text, sec.tag)

        #Rellenar la Lista Visual de Elementos
        for ele in manager.get_all_elements():
            display_text = f"Elem {ele.tag}: (Nodo {ele.node_i} -> Nodo {ele.node_j})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, ele.tag)
            self.list_elements.addItem(item)

    def on_add_element_clicked(self):
        """ Logica para tomar la UI, validar y crer el ForcebeamColumn """

        #1. Extraemos los IDs reales que guardamos en los comboBoxes

        i_node_tag = self.cb_node_i.currentData()
        j_node_tag = self.cb_node_j.currentData()
        sec_tag = self.cb_section.currentData()

        #Verificamos que exitan los nodos y secciones

        if i_node_tag is None or j_node_tag is None or sec_tag is None:
            QMessageBox.warning(self, "Datos Incompletos", "Asegurese de haber creaado al menos 2 Nodos y una sección.")
            return
        
        # Verificamos que la longitud no sea 0.return

        if i_node_tag == j_node_tag:
            QMessageBox.warning(self, "Error de Geometría", "El nodo inicial y final no pueden ser iguales.")
            return

        # Extraemos parámetros enteros
        transf_tag = self.spin_transf.value()
        int_pts = self.spin_int_pts.value()

        manager = ProjectManager.instance()
        next_tag = manager.get_next_element_tag()

        #Intansiamos el objetor elemento usando la clase ForceBeamColumn

        new_element = ForceBeamColumn(

            tag = next_tag,
            node_i = i_node_tag,
            node_j = j_node_tag,
            section_tag = sec_tag,
            transf_tag = transf_tag,
            integration_points = int_pts,
            mass_density = 0.0
        )

        #Asignamos la masa automatic consultale a la sección
        section = manager.get_section(sec_tag)
        if section:
            new_element.mass_density = section.get_mass_per_length(manager)

        #Pasamos el elementos al manager para que lo guarde
        manager.add_element(new_element)
        manager.dataChanged.emit()
        self.load_data()

    def on_element_selected(self, item):
        tag = item.data(Qt.ItemDataRole.UserRole)
        manager = ProjectManager.instance()
        ele = manager.get_element(tag)
        if ele:
            idx_i = self.cb_node_i.findData(ele.node_i)
            if idx_i >= 0: self.cb_node_i.setCurrentIndex(idx_i)
            
            idx_j = self.cb_node_j.findData(ele.node_j)
            if idx_j >= 0: self.cb_node_j.setCurrentIndex(idx_j)
            
            idx_sec = self.cb_section.findData(ele.section_tag)
            if idx_sec >= 0: self.cb_section.setCurrentIndex(idx_sec)
            
            self.spin_transf.setValue(ele.transf_tag)
            self.spin_int_pts.setValue(ele.integration_points)

    def delete_element(self):
        current_row = self.list_elements.currentRow()
        if current_row < 0: return

        item = self.list_elements.item(current_row)
        tag_to_delete = item.data(Qt.ItemDataRole.UserRole)

        manager = ProjectManager.instance()
        manager.delete_element(tag_to_delete)
        manager.dataChanged.emit()
        self.load_data()

    def update_element(self):
        current_row = self.list_elements.currentRow()
        if current_row < 0: return 

        item = self.list_elements.item(current_row)
        tag_to_modify = item.data(Qt.ItemDataRole.UserRole)

        manager = ProjectManager.instance()
        ele = manager.get_element(tag_to_modify)

        if ele:
            ele.node_i = self.cb_node_i.currentData()
            ele.node_j = self.cb_node_j.currentData()
            ele.section_tag = self.cb_section.currentData()
            ele.transf_tag = self.spin_transf.value()
            ele.integration_points = self.spin_int_pts.value()

            section = manager.get_section(ele.section_tag)
            if section:
                ele.mass_density = section.get_mass_per_length(manager)

            manager.dataChanged.emit()
            self.load_data()
            
            # Restaurar la selección
            for i in range(self.list_elements.count()):
                list_item = self.list_elements.item(i)
                if list_item.data(Qt.ItemDataRole.UserRole) == tag_to_modify:
                    self.list_elements.setCurrentItem(list_item)
                    break


    def on_tab_changed(self, index):
        """ Se dispara cada vez que el usuario cambia de pestaña """
    
        if index == 1:
            self.load_data()

    
    

