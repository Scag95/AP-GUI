import math
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QPushButton,QListWidgetItem)
from PyQt6.QtCore import Qt

from src.analysis.manager import ProjectManager
from src.ui.widgets.section_forms import SectionForm
from src.analysis.sections import FiberSection, RectPatch, LayerStraight
from src.ui.widgets.section_preview import SectionPreview

class SectionDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Definir Secciones")
        self.resize(800,600)
        
        #Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
 
        self.main_layout = QHBoxLayout(self)

        #Panel Izquierdo (Lista)
        self.left_panel_layout = QVBoxLayout()
        self.sections_list  = QListWidget()
        self.left_panel_layout.addWidget(self.sections_list)

        #Botones de control
        self.btn_add = QPushButton("Añadir sección")
        self.btn_delete =QPushButton("Borrar sección")
        self.left_panel_layout.addWidget(self.btn_add)
        self.left_panel_layout.addWidget(self.btn_delete)

        #Añadimos el Panel izquierdo al layout principal
        self.main_layout.addLayout(self.left_panel_layout, stretch=1)

        #Añadimos el Panel derecho al layout principal
        self.right_panel_layout = QVBoxLayout()
        self.form_section = SectionForm()
        self.right_panel_layout.addWidget(self.form_section)

        #Añadimos el panel derefcho a layout principal
        self.main_layout.addLayout(self.right_panel_layout, stretch=2)

        #Añadimos el panel de previsualización de la sección.
        self.preview_widget = SectionPreview()
        self.preview_widget.setFixedHeight(300)
        self.preview_widget.setFixedWidth(300)
        self.main_layout.addWidget(self.preview_widget, stretch=3)

        #conectamos los botones
        self.btn_add.clicked.connect(self.add_section)
        self.btn_delete.clicked.connect(self.delete_section)

        #conectamos la señal para actualizar los campos
        self.sections_list.itemClicked.connect(self.on_section_selected)
        #cargar secciones existentes
        self.load_sections()

        # --- CONEXIÓN DE SEÑALES PARA PREVIEW (NUEVO) ---
        # Conectamos todos los inputs relevantes al método update_preview
        # Dimensiones
        self.form_section.spin_h.valueChanged.connect(self.update_preview)
        self.form_section.spin_b.valueChanged.connect(self.update_preview)
        self.form_section.spin_cover.valueChanged.connect(self.update_preview)
        
        # Cantidades de acero
        self.form_section.spin_top_qty.valueChanged.connect(self.update_preview)
        self.form_section.spin_bot_qty.valueChanged.connect(self.update_preview)

        # Diamentro
        self.form_section.spin_top_diam.valueChanged.connect(self.update_preview)
        self.form_section.spin_bot_diam.valueChanged.connect(self.update_preview)
        
        # Materiales (Combos)
        self.form_section.combo_concrete.currentIndexChanged.connect(self.update_preview)
        self.form_section.combo_steel.currentIndexChanged.connect(self.update_preview)
        
        # Primera llamada para que no salga vacío al abrir
        self.update_preview()      

    def add_section(self):

        #1. Recolectar la información de la sección
        data = self.form_section.get_data()

        #Validamos que tengamos materiales creados
        if data['concrete'] is None or data['steel'] is None:
            print("Error: Debes de tener materiales")
            return
        
        #2. Preramos ls variables
        b = data['b']
        h = data['h']
        cover = data['cover'] 
        mat_conc = data['concrete']
        mat_steel = data['steel']
        
        # 3. Crear la Sección
        #Llamamos del ProjectManager el tag del material.
        manager = ProjectManager.instance()
        tag = manager.get_next_section_tag()
        
        # Si el usuario no puso nombre, generamos uno
        name = self.form_section.textbox_name.text()
        if not name:
            name = f"Sec_{b}x{h}"

        section = FiberSection(tag, name)

        #4. Creamos la geometría de la sección (Concreto)
        section.add_rect_patch(RectPatch(
            material_tag = mat_conc,
            yI= round(-h/2, 6), zI= round(-b/2, 6),
            yJ=  round(h/2, 6), zJ=  round(b/2, 6)
        ))

        #5. Creamos las barras de acero
        #Capa superior
        if data['top_qty'] >0:
            area_top = (math.pi * (data['top_diam']**2))/4
            section.add_layer_straight(LayerStraight(
                material_tag = mat_steel,
                num_bars = data['top_qty'],
                area_bar = area_top,
                yStart = round(h/2 - cover, 6), zStart = round(-b/2 + cover, 6),
                yEnd   = round(h/2 - cover, 6), zEnd   =  round(b/2 - cover, 6)
            ))
        # Capa INFERIOR
        if data['bot_qty'] > 0:
            area_bot = (math.pi * (data['bot_diam']**2)) / 4
            section.add_layer_straight(LayerStraight(
                material_tag=mat_steel,
                num_bars=data['bot_qty'],
                area_bar=area_bot,
                yStart= round(-h/2 + cover, 6), zStart= round(-b/2 + cover, 6),
                yEnd  = round(-h/2 + cover, 6), zEnd  =  round(b/2 - cover, 6)
            ))



        # 6. Guardar y Actualizar UI
        manager.add_section(section)
        #Acutalizar la lista en la UI
        display_text = f"{tag}-{name}"

        #Guardamos el ID del material en una "mochila"
        item=QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, tag)
        self.sections_list.addItem(item)

        print(f"[DEBUG] Sección Creada: {name} | Arg: {data}")

    def delete_section(self):
        current_row = self.sections_list.currentRow()
        manager = ProjectManager.instance()
        if current_row >=0:
            item = self.sections_list.item(current_row)
            tag_to_delete = item.data(Qt.ItemDataRole.UserRole)

            if tag_to_delete is not None:
                manager.delete_section(tag_to_delete)
            self.sections_list.takeItem(current_row)
            del item

    def load_sections(self):
        self.sections_list.clear()
        manager = ProjectManager.instance()
        sections = manager.get_all_sections()

        for  section in sections:
            display_text = f"{section.tag}-{section.name}"
            #Guardamos el ID del material en una "mochila"
            item=QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, section.tag)
            self.sections_list.addItem(item)

 
    def update_preview(self):
        #1. Crea una sección temporal
        temp_section = self._build_section_from_form()

        if temp_section:
            self.preview_widget.plot_section(temp_section)
        else:
            pass

    def _build_section_from_form(self):
        """
        Crea un objeto FiberSection TEMPORAL con los datos actuales del formulario.
        No lo guarda en el Manager. Retorna None si faltan datos.
        """
        data = self.form_section.get_data()
        
        # Validamos materiales
        if data['concrete'] is None or data['steel'] is None:
            return None
            
        b = data['b']
        h = data['h']
        cover = data['cover']
        mat_conc = data['concrete']
        mat_steel = data['steel']
        
        # Nombre temporal (o real)
        tag = 0 # Dummy tag para preview
        name = self.form_section.textbox_name.text() or f"SecPV_{b}x{h}"
        
        section = FiberSection(tag, name)
        
        # --- Lógica de Geometría (Copiada/Movida de add_section) ---
        # 4. Crear la geometría de la sección (Concreto)
        section.add_rect_patch(RectPatch(
            material_tag = mat_conc,
            yI= round(-h/2, 6), zI= round(-b/2, 6),
            yJ=  round(h/2, 6), zJ=  round(b/2, 6)
        ))
        # 5. Crear las barras de acero
        # Capa superior
        if data['top_qty'] > 0:
            area_top = (math.pi * (data['top_diam']**2))/4
            section.add_layer_straight(LayerStraight(
                material_tag = mat_steel,
                num_bars = data['top_qty'],
                area_bar = area_top,
                yStart = round(h/2 - cover, 6), zStart = round(-b/2 + cover, 6),
                yEnd   = round(h/2 - cover, 6), zEnd   =  round(b/2 - cover, 6)
            ))
            
        # Capa INFERIOR
        if data['bot_qty'] > 0:
            area_bot = (math.pi * (data['bot_diam']**2)) / 4
            section.add_layer_straight(LayerStraight(
                material_tag=mat_steel,
                num_bars=data['bot_qty'],
                area_bar=area_bot,
                yStart= round(-h/2 + cover, 6), zStart= round(-b/2 + cover, 6),
                yEnd  = round(-h/2 + cover, 6), zEnd  =  round(b/2 - cover, 6)
            ))
            
        return section
    def on_section_selected(self, item):
        tag = item.data(Qt.ItemDataRole.UserRole)
        manager = ProjectManager.instance()
        section = manager.get_section(tag)
        
        if section and isinstance(section, FiberSection):
            self.form_section.set_data(section)
            # Forzamos update de la preview
            self.update_preview()
