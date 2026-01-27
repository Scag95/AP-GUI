from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QListWidgetItem, QDoubleSpinBox, 
                             QPushButton, QGroupBox, QFormLayout, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
from src.analysis.manager import ProjectManager
from src.analysis.loads import NodalLoad

class NodalLoadsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asignar Cargas Nodales")
        self.resize(600, 450)
        self.manager = ProjectManager.instance()

        layout = QHBoxLayout(self)

        # --- Panel Izquierdo: Selección de Nodos ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Nodos (coma/rangos):"))
        self.txt_nodes = QLineEdit()
        self.txt_nodes.setPlaceholderText("1,2,5-9")
        self.txt_nodes.returnPressed.connect(self.select_from_text)
        left_layout.addWidget(self.txt_nodes)

        left_layout.addWidget(QLabel("Lista de Nodos:"))
        self.node_list = QListWidget()
        self.node_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        left_layout.addWidget(self.node_list)
        
        layout.addLayout(left_layout, stretch=1)

        # --- Panel Derecho: Configuración de Carga ---
        right_layout = QVBoxLayout()

        self.load_group = QGroupBox("Fuerzas y Momentos")
        form_layout = QFormLayout()

        # Input Fx
        self.fx_input = QDoubleSpinBox()
        self.fx_input.setRange(-1e6, 1e6)
        self.fx_input.setDecimals(2)
        self.fx_input.setSuffix(" kN")
        
        # Input Fy
        self.fy_input = QDoubleSpinBox()
        self.fy_input.setRange(-1e6, 1e6)
        self.fy_input.setDecimals(2)
        self.fy_input.setSuffix(" kN")
        
        # Input Mz
        self.mz_input = QDoubleSpinBox()
        self.mz_input.setRange(-1e8, 1e8)
        self.mz_input.setDecimals(2)
        self.mz_input.setSuffix(" kNm")

        form_layout.addRow("Fuerza X (Fx):", self.fx_input)
        form_layout.addRow("Fuerza Y (Fy):", self.fy_input)
        form_layout.addRow("Momento Z (Mz):", self.mz_input)
        
        self.load_group.setLayout(form_layout)
        right_layout.addWidget(self.load_group)

        # Botones
        self.btn_apply = QPushButton("Aplicar Carga")
        self.btn_apply.clicked.connect(self.apply_loads)
        right_layout.addWidget(self.btn_apply)

        self.btn_clear = QPushButton("Borrar Cargas Seleccionadas")
        self.btn_clear.clicked.connect(self.clear_loads)
        right_layout.addWidget(self.btn_clear)

        right_layout.addStretch()
        layout.addLayout(right_layout, stretch=1)

        # Inicializar
        self.populate_nodes()

    def populate_nodes(self):
        self.node_list.clear()
        nodes = self.manager.get_all_nodes()
        loads = self.manager.get_all_loads()

        # Mapa rápido {node_tag: load_obj}
        node_load_map = {}
        for load in loads:
            if isinstance(load, NodalLoad):
                node_load_map[load.node_tag] = load

        for n in nodes:
            item = QListWidgetItem(f"Nodo {n.tag}")
            item.setData(Qt.ItemDataRole.UserRole, n.tag)
            
            if n.tag in node_load_map:
                l = node_load_map[n.tag]
                item.setText(f"Nodo {n.tag} [Fx={l.fx}, Fy={l.fy}, Mz={l.mz}]")
                # Opcional: item.setBackground(Qt.GlobalColor.lightGray)

            self.node_list.addItem(item)

    def select_from_text(self):
        text = self.txt_nodes.text()
        ids = self._parse_input(text)
        self.node_list.clearSelection()
        for i in range(self.node_list.count()):
            item = self.node_list.item(i)
            tag = item.data(Qt.ItemDataRole.UserRole)
            if tag in ids:
                item.setSelected(True)

    def _parse_input(self, text):
        # Misma lógica que en ElementLoadsDialog
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
                    if start > end: start, end = end, start
                    for i in range(start, end + 1):
                        ids.add(i)
                except ValueError:
                    pass
            elif p.isdigit():
                ids.add(int(p))
        return list(ids)

    def apply_loads(self):
        target_ids = self._parse_input(self.txt_nodes.text())
        if not target_ids:
            selected_items = self.node_list.selectedItems()
            for item in selected_items:
                target_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        target_ids = list(set(target_ids)) # Unicos

        if not target_ids:
            QMessageBox.warning(self, "Aviso", "Selecciona nodos.")
            return

        fx = self.fx_input.value()
        fy = self.fy_input.value()
        mz = self.mz_input.value()

        count = 0
        for node_tag in target_ids:
            if not self.manager.get_node(node_tag):
                continue
            
            # Quitar carga previa
            self._remove_load_for_node(node_tag)

            # Nueva carga
            new_tag = self.manager.get_next_load_tag()
            load = NodalLoad(new_tag, node_tag, fx, fy, mz)
            self.manager.add_load(load)
            count += 1
        
        self.populate_nodes()
        QMessageBox.information(self, "Éxito", f"Carga aplicada a {count} nodos.")

    def clear_loads(self):
        target_ids = self._parse_input(self.txt_nodes.text())
        if not target_ids:
            selected_items = self.node_list.selectedItems()
            for item in selected_items:
                target_ids.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not target_ids: return

        for node_tag in target_ids:
            self._remove_load_for_node(node_tag)
        
        self.populate_nodes()

    def _remove_load_for_node(self, node_tag):
        loads = self.manager.get_all_loads()
        for load in loads:
            if isinstance(load, NodalLoad) and load.node_tag == node_tag:
                self.manager.delete_load(load.tag)