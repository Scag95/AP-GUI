from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QCheckBox, QPushButton, QLabel, QLineEdit, 
                             QListWidget, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt
from src.analysis.manager import ProjectManager

class RestraintsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = ProjectManager.instance()
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        self.setWindowTitle("Restricciones de Nodos (2D)")
        root = QVBoxLayout(self)

        # Entrada de nodos
        row_nodes = QHBoxLayout()
        row_nodes.addWidget(QLabel("Nodos (coma/rangos):"))
        self.txt_nodes = QLineEdit(self)
        self.txt_nodes.setPlaceholderText("1,2,5-9")
        row_nodes.addWidget(self.txt_nodes)
        root.addLayout(row_nodes)

        # Botones rápidos (borde)
        row_quick = QHBoxLayout()
        self.btn_all = QPushButton("Todos", self)
        self.btn_bottom = QPushButton("Borde inferior", self)
        
        row_quick.addWidget(self.btn_all)
        row_quick.addWidget(self.btn_bottom)
        root.addLayout(row_quick)

        # DOFs
        row_dofs = QHBoxLayout()
        row_dofs.addWidget(QLabel("Restringir:"))
        self.chk_ux = QCheckBox("UX", self)
        self.chk_uy = QCheckBox("UY", self)
        self.chk_rz = QCheckBox("RZ", self)
        for c in (self.chk_ux, self.chk_uy, self.chk_rz):
            row_dofs.addWidget(c)
        root.addLayout(row_dofs)

        # Lista
        self.lst = QListWidget(self)
        self.lst.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # self.lst.currentRowChanged.connect(self._load_selected_to_form) 
        # (Opcional: Si queremos que al clickar en la lista se actualicen los checkboxes)
        root.addWidget(self.lst)

        # Acciones (dos filas)
        row_actions_top = QHBoxLayout()
        self.btn_apply = QPushButton("Aplicar / Actualizar", self)
        self.btn_remove = QPushButton("Quitar Restricción", self)
        
        row_actions_top.addWidget(self.btn_apply)
        row_actions_top.addWidget(self.btn_remove)
        root.addLayout(row_actions_top)

        row_actions_bottom = QHBoxLayout()
        self.btn_accept = QPushButton("Cerrar", self) # Equivalente a Aceptar/Salir
        
        row_actions_bottom.addWidget(self.btn_accept)
        root.addLayout(row_actions_bottom)

        # Conexiones
        self.btn_all.clicked.connect(lambda: self._quick_select('all'))
        self.btn_bottom.clicked.connect(lambda: self._quick_select('bottom'))

        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_remove.clicked.connect(self._on_remove)
        self.btn_accept.clicked.connect(self.accept)

        self.resize(520, 420)

    # --- Lógica Interna ---

    def _quick_select(self, mode):
        nodes = []
        all_nodes = self.manager.get_all_nodes()
        
        if mode == 'all':
            nodes = [str(n.tag) for n in all_nodes]
        elif mode == 'bottom':
            # Buscar Y mínima
            min_y = min((n.y for n in all_nodes), default=0)
            # Buscar nodos con esa Y (tolerancia 1e-4)
            nodes = [str(n.tag) for n in all_nodes if abs(n.y - min_y) < 1e-4]
            
        self.txt_nodes.setText(",".join(nodes))

    def _parse_node_input(self):
        text = self.txt_nodes.text().strip()
        if not text: return []
        
        ids = set()
        parts = text.split(',')
        for p in parts:
            p = p.strip()
            if '-' in p:
                try:
                    start, end = map(int, p.split('-'))
                    for i in range(start, end + 1):
                        ids.add(i)
                except ValueError:
                    pass
            elif p.isdigit():
                ids.add(int(p))
        return list(ids)

    def _on_apply(self):
        # 1. Leer IDs
        target_ids = self._parse_node_input()
        if not target_ids:
            QMessageBox.warning(self, "Aviso", "No hay nodos seleccionados.")
            return

        # 2. Leer Fixity
        fixity = [
            1 if self.chk_ux.isChecked() else 0,
            1 if self.chk_uy.isChecked() else 0,
            1 if self.chk_rz.isChecked() else 0
        ]
        
        # 3. Aplicar a cada nodo
        count = 0
        for tag in target_ids:
            node = self.manager.get_node(tag)
            if node:
                node.fixity = fixity
                count += 1
        
        # 4. Refrescar UI
        self.manager.dataChanged.emit() # Avisar a la MainWindow que refresque gráficos
        self._refresh_list()
        QMessageBox.information(self, "Info", f"Restricciones aplicadas a {count} nodo(s).")

    def _on_remove(self):
        # Quita las restricciones (pone [0,0,0]) a los items seleccionados en la LISTA
        selected_items = self.lst.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            # El texto es "Nodo X: [1, 1, 1]"
            try:
                tag = int(item.text().split(':')[0].replace("Nodo ", ""))
                node = self.manager.get_node(tag)
                if node:
                    node.fixity = [0, 0, 0]
            except:
                pass
        
        self.manager.dataChanged.emit()
        self._refresh_list()

    def _refresh_list(self):
        self.lst.clear()
        # Listar solo nodos que tengan alguna restricción
        for node in self.manager.get_all_nodes():
            if any(node.fixity): # Si alguno es 1
                fix_str = str(node.fixity) # "[1, 1, 0]"
                item_text = f"Nodo {node.tag}: {fix_str}"
                self.lst.addItem(item_text)
