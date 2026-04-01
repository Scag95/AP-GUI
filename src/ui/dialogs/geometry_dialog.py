from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QLabel, QDoubleSpinBox, QSpinBox, QComboBox, QPushButton, QHBoxLayout, QFormLayout, QCheckBox
)
from PyQt6.QtCore import Qt
from src.analysis.manager import ProjectManager
from src.analysis.node import Node
from src.analysis.element import ForceBeamColumn, ForceBeamColumnHinge
from src.ui.widgets.unit_spinbox import UnitSpinBox
from src.utils.units import UnitType



class GeometryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir Nodos y Elementos")
        self.resize(800,600)

        #Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.main_layout = QHBoxLayout(self)

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

        # --- Checkbox de masa ---
        self.chk_mass = QCheckBox("Asignar masa nodal")
        form_layout.addRow(self.chk_mass)

        #--- Campos de masa ---
        self.widget_mass = QWidget()
        mass_layout = QFormLayout(self.widget_mass)
        self.widget_mass.setVisible(False)

        self.spin_mx = UnitSpinBox(UnitType.MASS)
        self.spin_mx.setRange(0.0, 99999999.0)
        self.spin_mx.setDecimals(6)
        self.spin_my = UnitSpinBox(UnitType.MASS)
        self.spin_my.setRange(0.0, 99999999.0)
        self.spin_my.setDecimals(6)
        self.spin_mrz = UnitSpinBox(UnitType.MASS)
        self.spin_mrz.setRange(0.0, 99999999.0)
        self.spin_mrz.setDecimals(6)
        
        mass_layout.addRow("Masa X:", self.spin_mx)
        mass_layout.addRow("Masa Y:", self.spin_my)
        mass_layout.addRow("Masa Rot. Z:", self.spin_mrz)

        form_layout.addRow(self.widget_mass)

        self.chk_mass.toggled.connect(self.widget_mass.setVisible)

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


        #Leer masa si el checkbox está activado
        if self.chk_mass.isChecked():
            mass = [
                self.spin_mx.get_value_base(),
                self.spin_my.get_value_base(),
                self.spin_mrz.get_value_base()
            ]

        else:
            mass = None

        # Le pedimos al Manager el siguiente tag del nodo
        manager = ProjectManager.instance()
        next_tag = manager.get_next_node_tag()

        #Creamos el nodo 
        new_node = Node(next_tag, x_val, y_val, mass=mass)

        #Se lo pasamos al manager para que lo almacene
        manager.add_node(new_node)
        manager.dataChanged.emit()

        #Limpiamos los spinbox
        self.spin_x.set_value_base(0.0)
        self.spin_y.set_value_base(0.0)
        self.chk_mass.setChecked(False)
        self.spin_mx.set_value_base(0.0)
        self.spin_my.set_value_base(0.0)
        self.spin_mrz.set_value_base(0.0)
        self.spin_x.setFocus()
        self.refresh_node_list()


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
        """ Rellena el formulario al seleccionar un nodo de la lista """
        tag = item.data(Qt.ItemDataRole.UserRole)
        manager = ProjectManager.instance()
        node = manager.get_node(tag)
        
        if not node:
            return
            
        self.spin_x.set_value_base(node.x)
        self.spin_y.set_value_base(node.y)

        # Rellenar masa si el nodo la tiene
        if node.mass is not None:
            self.chk_mass.setChecked(True)      #Esto dispara setVisible(true) automáticamente.
            self.spin_mx.set_value_base(node.mass[0])
            self.spin_my.set_value_base(node.mass[1])
            self.spin_mrz.set_value_base(node.mass[2])
        else:
            self.chk_mass.setChecked(False)  #Oculta el wifget_mass automáticamente

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

        if not node: return

        node.x = self.spin_x.get_value_base()
        node.y = self.spin_y.get_value_base()

        if self.chk_mass.isChecked():
            node.mass = [
                self.spin_mx.get_value_base(),
                self.spin_my.get_value_base(),
                self.spin_mrz.get_value_base()
            ]
        else:
            node.mass = None

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

# --- Comboboxes para seleccionar recursos existentes ---
        self.cb_element_type = QComboBox()
        self.cb_element_type.addItems(["ForceBeamColumn", "ForceBeamColumnHinge"])
        self.cb_element_type.currentTextChanged.connect(self.on_element_type_changed)
        self.cb_node_i = QComboBox()
        self.cb_node_j = QComboBox()
        self.cb_section = QComboBox() # Será la sección Estandar o Elástica

        # --- Bloque oculto para HingeRadau ---
        self.widget_hinge = QWidget()
        hinge_layout = QFormLayout(self.widget_hinge)
        
        self.cb_section_i = QComboBox()
        self.cb_section_j = QComboBox()
        self.spin_lp_i = QDoubleSpinBox()
        self.spin_lp_i.setDecimals(4)
        self.spin_lp_i.setRange(0.0001, 999.0)
        self.spin_lp_j = QDoubleSpinBox()
        self.spin_lp_j.setDecimals(4)
        self.spin_lp_j.setRange(0.0001, 999.0)
        hinge_layout.addRow("Sección Rótula I:", self.cb_section_i)
        hinge_layout.addRow("Longitud Rótula I (lp_i):", self.spin_lp_i)
        hinge_layout.addRow("Sección Rótula J:", self.cb_section_j)
        hinge_layout.addRow("Longitud Rótula J (lp_j):", self.spin_lp_j)
        self.widget_hinge.setVisible(False)

        # --- Spinboxes de OpenSees ---
        self.spin_transf = QSpinBox()
        self.spin_transf.setRange(1,999)
        self.spin_transf.setValue(1)
        
        self.spin_int_pts = QSpinBox()
        self.spin_int_pts.setRange(1,10)
        self.spin_int_pts.setValue(5)

        # --- Añadir al Layout Principal del panel ---
        form_layout.addRow("Tipo de Elemento", self.cb_element_type)
        form_layout.addRow("Nodo Inicial", self.cb_node_i)
        form_layout.addRow("Nodo Final", self.cb_node_j)
        
        self.lbl_section = QLabel("Sección Transversal")
        form_layout.addRow(self.lbl_section, self.cb_section)
        
        form_layout.addRow(self.widget_hinge) # Agregamos el sub-formulario oculto
        form_layout.addRow("Tag Transf. Geométrica", self.spin_transf)
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
# Limpiar por si se llama múltiples veces
        self.cb_node_i.clear()
        self.cb_node_j.clear()
        self.cb_section.clear()
        self.cb_section_i.clear()
        self.cb_section_j.clear()
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
            self.cb_section_i.addItem(display_text, sec.tag)
            self.cb_section_j.addItem(display_text, sec.tag)

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

        # Intanciamos el objeto elemento usando la clase seleccionada en la UI
        element_type = self.cb_element_type.currentText()
        if element_type == "ForceBeamColumnHinge":
            new_element = ForceBeamColumnHinge(
                tag = next_tag,
                node_i = i_node_tag,
                node_j = j_node_tag,
                transf_tag = transf_tag,
                section_i_tag = self.cb_section_i.currentData(),
                lp_i = self.spin_lp_i.value(),
                section_j_tag = self.cb_section_j.currentData(),
                lp_j = self.spin_lp_j.value(),
                section_e_tag = sec_tag,
                mass_density = 0.0
            )
        else:
            new_element = ForceBeamColumn(
                tag = next_tag,
                node_i = i_node_tag,
                node_j = j_node_tag,
                section_tag = sec_tag,
                transf_tag = transf_tag,
                integration_points = int_pts,
                mass_density = 0.0
            )

        # Asignamos la masa automatica consultale a la sección
        section = manager.get_section(sec_tag)
        if section:
            new_element.mass_density = section.get_mass_per_length(manager)

        # Pasamos el elemento al manager para que lo guarde
        manager.add_element(new_element)
        manager.dataChanged.emit()
        self.load_data()

    def on_element_selected(self, item):
        tag = item.data(Qt.ItemDataRole.UserRole)
        manager = ProjectManager.instance()
        ele = manager.get_element(tag)
        if not ele: return
        
        idx_i = self.cb_node_i.findData(ele.node_i)
        if idx_i >= 0: self.cb_node_i.setCurrentIndex(idx_i)
        
        idx_j = self.cb_node_j.findData(ele.node_j)
        if idx_j >= 0: self.cb_node_j.setCurrentIndex(idx_j)
        
        if isinstance(ele, ForceBeamColumnHinge):
            self.cb_element_type.setCurrentText("ForceBeamColumnHinge")
            
            idx_sec_e = self.cb_section.findData(ele.section_e_tag)
            if idx_sec_e >= 0: self.cb_section.setCurrentIndex(idx_sec_e)
            
            idx_sec_i = self.cb_section_i.findData(ele.section_i_tag)
            if idx_sec_i >= 0: self.cb_section_i.setCurrentIndex(idx_sec_i)
            
            idx_sec_j = self.cb_section_j.findData(ele.section_j_tag)
            if idx_sec_j >= 0: self.cb_section_j.setCurrentIndex(idx_sec_j)
            
            self.spin_lp_i.setValue(ele.lp_i)
            self.spin_lp_j.setValue(ele.lp_j)
            
            self.spin_int_pts.setEnabled(False) # Las rótulas no usan este parámetro
        else:
            self.cb_element_type.setCurrentText("ForceBeamColumn")
            idx_sec = self.cb_section.findData(ele.section_tag)
            if idx_sec >= 0: self.cb_section.setCurrentIndex(idx_sec)
            
            self.spin_int_pts.setEnabled(True)
            self.spin_int_pts.setValue(getattr(ele, 'integration_points', 5))
        
        self.spin_transf.setValue(ele.transf_tag)

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

        if not ele: return

        i_node_tag = self.cb_node_i.currentData()
        j_node_tag = self.cb_node_j.currentData()
        sec_tag = self.cb_section.currentData()
        transf_tag = self.spin_transf.value()
        int_pts = self.spin_int_pts.value()

        # Instanciamos un elemento nuevo para permitir cambiar el tipo al vuelo
        element_type = self.cb_element_type.currentText()
        if element_type == "ForceBeamColumnHinge":
            new_ele = ForceBeamColumnHinge(
                tag = tag_to_modify,  # Mismo tag original
                node_i = i_node_tag,
                node_j = j_node_tag,
                transf_tag = transf_tag,
                section_i_tag = self.cb_section_i.currentData(),
                lp_i = self.spin_lp_i.value(),
                section_j_tag = self.cb_section_j.currentData(),
                lp_j = self.spin_lp_j.value(),
                section_e_tag = sec_tag,
                mass_density = 0.0
            )
        else:
            new_ele = ForceBeamColumn(
                tag = tag_to_modify,
                node_i = i_node_tag,
                node_j = j_node_tag,
                section_tag = sec_tag,
                transf_tag = transf_tag,
                integration_points = int_pts,
                mass_density = 0.0
            )

        section = manager.get_section(sec_tag)
        if section:
            new_ele.mass_density = section.get_mass_per_length(manager)

        # Sustituimos el elemento antiguo de forma limpia en el diccionario interno
        manager.elements[tag_to_modify] = new_ele

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

    def on_element_type_changed(self, text):
        if text == "ForceBeamColumnHinge":
            self.lbl_section.setText("Sección Tramo Central (e):")
            self.widget_hinge.setVisible(True)
        else:
            self.lbl_section.setText("Sección Transversal:")
            self.widget_hinge.setVisible(False)    
    

