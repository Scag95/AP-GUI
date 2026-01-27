from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QListWidgetItem, QDoubleSpinBox, 
                             QPushButton, QGroupBox, QFormLayout, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
from src.analysis.manager import ProjectManager
from src.analysis.loads import ElementLoad

class ElementLoadsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asignar Cargas en Elementos")
        self.resize(600, 400)
        self.manager = ProjectManager.instance()

        # Layout principal horizontal
        layout = QHBoxLayout(self)

        # --- Panel Izquierdo: Selección ---
        left_layout = QVBoxLayout()
        
        # 1. Input de texto para selección avanzada
        left_layout.addWidget(QLabel("Elementos (coma/rangos):"))
        self.txt_elements = QLineEdit()
        self.txt_elements.setPlaceholderText("1,2,5-9")
        # Tip: Si pulsas Enter en el cuadro de texto, se seleccionan en la lista visual
        self.txt_elements.returnPressed.connect(self.select_from_text)
        left_layout.addWidget(self.txt_elements)

        left_layout.addWidget(QLabel("Lista de Elementos:"))
        self.element_list = QListWidget()
        self.element_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        # Sincronizar: al clicar en la lista, actualizar el texto (opcional, puede ser complejo bidireccional)
        left_layout.addWidget(self.element_list)
        
        layout.addLayout(left_layout, stretch=1)

        # --- Panel Derecho: Configuración ---
        right_layout = QVBoxLayout()

        self.load_group = QGroupBox("Carga Distribuida Uniforme")
        form_layout = QFormLayout()

        # Inputs
        self.wx_input = QDoubleSpinBox()
        self.wx_input.setRange(-1e6, 1e6)
        self.wx_input.setDecimals(2)
        self.wx_input.setSuffix(" kN/m") 

        self.wy_input = QDoubleSpinBox()
        self.wy_input.setRange(-1e6, 1e6)
        self.wy_input.setDecimals(2)
        self.wy_input.setSuffix(" kN/m") 

        form_layout.addRow("Carga X (wx):", self.wx_input)
        form_layout.addRow("Carga Y (wy):", self.wy_input)
        self.load_group.setLayout(form_layout)

        right_layout.addWidget(self.load_group)

        # Botones
        self.btn_apply = QPushButton("Aplicar carga")
        self.btn_apply.clicked.connect(self.apply_loads) 
        right_layout.addWidget(self.btn_apply)

        self.btn_clear = QPushButton("Borrar Cargas Seleccionadas")
        self.btn_clear.clicked.connect(self.clear_loads)
        right_layout.addWidget(self.btn_clear)

        right_layout.addStretch()
        layout.addLayout(right_layout, stretch=1)

        # Inicializar datos
        self.populate_elements()

    def populate_elements(self):
        self.element_list.clear()
        elements = self.manager.get_all_elements()
        loads = self.manager.get_all_loads()

        element_load_map = {}
        for load in loads:
            if isinstance(load, ElementLoad):
                element_load_map[load.element_tag] = load

        for el in elements:
            item = QListWidgetItem(f"Elemento {el.tag}")
            item.setData(Qt.ItemDataRole.UserRole, el.tag)

            if el.tag in element_load_map:
                l = element_load_map[el.tag]
                item.setText(f"Elemento {el.tag} [Wx={l.wx}, Wy={l.wy}]")

            self.element_list.addItem(item)

    def select_from_text(self):
        """Selecciona visualmente en la lista los elementos escritos en el cuadro de texto."""
        text = self.txt_elements.text()
        ids = self._parse_input(text)
        
        # Limpiar selección actual
        self.element_list.clearSelection()

        # Seleccionar filas correspondientes
        for i in range(self.element_list.count()):
            item = self.element_list.item(i)
            tag = item.data(Qt.ItemDataRole.UserRole)
            if tag in ids:
                item.setSelected(True)

    def _parse_input(self, text):
        """Convierte '1,3-5' en [1, 3, 4, 5]"""
        text = text.strip()
        if not text: return []
        
        ids = set()
        parts = text.split(',')
        for p in parts:
            p = p.strip()
            if '-' in p:
                try:
                    start_s, end_s = p.split('-')
                    start, end = int(start_s), int(end_s)
                    # Asegurarse de ir de menor a mayor
                    if start > end: start, end = end, start
                    for i in range(start, end + 1):
                        ids.add(i)
                except ValueError:
                    pass
            elif p.isdigit():
                ids.add(int(p))
        return list(ids)

    def apply_loads(self):
        # 1. Primero intentamos leer del cuadro de texto
        target_ids = self._parse_input(self.txt_elements.text())

        # 2. Si el cuadro está vacío, usamos la selección visual de la lista
        if not target_ids:
            selected_items = self.element_list.selectedItems()
            for item in selected_items:
                target_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        # 3. Eliminar duplicados
        target_ids = list(set(target_ids))

        if not target_ids:
            QMessageBox.warning(self, "Aviso", "No hay elementos seleccionados (escribe IDs o selecciona en la lista).")
            return

        wx = self.wx_input.value()
        wy = self.wy_input.value()

        count = 0
        for el_tag in target_ids:
            # Verificar que el elemento existe
            if not self.manager.get_element(el_tag):
                continue

            self._remove_load_for_element(el_tag)

            # Crear nueva Carga
            new_tag = self.manager.get_next_load_tag()
            load = ElementLoad(new_tag, el_tag, wx, wy)
            self.manager.add_load(load)
            count += 1
        
        self.populate_elements()
        QMessageBox.information(self, "Éxito", f"Carga aplicada a {count} elementos.")

    def clear_loads(self):
        # Misma lógica: Texto o Selección Visual
        target_ids = self._parse_input(self.txt_elements.text())
        if not target_ids:
            selected_items = self.element_list.selectedItems()
            for item in selected_items:
                target_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not target_ids:
            return

        for el_tag in target_ids:
            self._remove_load_for_element(el_tag)

        self.populate_elements()

    def _remove_load_for_element(self, element_tag):
        loads = self.manager.get_all_loads() 
        for load in loads:
            if isinstance(load, ElementLoad) and load.element_tag == element_tag:
                self.manager.delete_load(load.tag)