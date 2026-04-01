from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QListWidgetItem, QDoubleSpinBox, 
                             QPushButton, QGroupBox, QFormLayout, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt
from src.analysis.manager import ProjectManager
from src.analysis.loads import LoadPattern

class PatternDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestor de Patrones de Carga")
        self.resize(800,600)

        #Centrar ventana al centro de la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        self.manager = ProjectManager.instance()

        layout = QHBoxLayout(self)

        # --- Panel Izquierdo: Lista de Patrones ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Pattern Existentes"))


        self.pattern_list = QListWidget()
        self.pattern_list.itemSelectionChanged.connect(self.on_pattern_selected)
        left_layout.addWidget(self.pattern_list)

        layout.addLayout(left_layout, stretch=1)

        # ---Panel Derecho: Edición de Datos ---
        right_layout = QVBoxLayout()

        self.group_box = QGroupBox("Porpiedades del Pattern")
        form_layout = QFormLayout()

        #Nombre del pattern
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Carga Viva")
        form_layout.addRow("Nombre:", self.name_input)

        #Multiplicador (-fact)
        self.factor_input = QDoubleSpinBox()
        self.factor_input.setRange(-100.0, 100.0)
        self.factor_input.setDecimals(3)
        self.factor_input.setSingleStep(0.1)
        self.factor_input.setValue(1.0) # Obligatorio Factor 1 por defecto
        form_layout.addRow("Factor (-fact):", self.factor_input)

        self.group_box.setLayout(form_layout)
        right_layout.addWidget(self.group_box)

        # Botones de Acción (CRUD)
        self.btn_add = QPushButton("Añadir Nuevo Patrón")
        self.btn_add.clicked.connect(self.add_pattern)
        right_layout.addWidget(self.btn_add)

        self.btn_update = QPushButton("Modificar Seleccionado")
        self.btn_update.clicked.connect(self.update_pattern)
        right_layout.addWidget(self.btn_update)

        self.btn_delete = QPushButton("Eliminar Patrón")
        self.btn_delete.clicked.connect(self.delete_pattern)
        right_layout.addWidget(self.btn_delete)

        right_layout.addStretch()
        layout.addLayout(right_layout, stretch=1)

        # Lanzar la carga inicial
        self.load_patterns()        

    def load_patterns(self):
        self.pattern_list.clear() #Limpiar vista actual

        for p in self.manager.get_all_patterns():
            item = QListWidgetItem(f"Pattern {p.tag}: {p.name} (Fact: {p.factor})")
            item.setData(Qt.ItemDataRole.UserRole, p.tag)
            self.pattern_list.addItem(item)

    def on_pattern_selected(self):
        selected = self.pattern_list.selectedItems()
        
        if not selected: return

        tag= selected[0].data(Qt.ItemDataRole.UserRole)
        pattern = self.manager.get_pattern(tag)
        if pattern:
            self.name_input.setText(pattern.name)
            self.factor_input.setValue(pattern.factor)

    def add_pattern(self):
        name = self.name_input.text().strip()
        factor = self.factor_input.value()
        tag = self.manager.get_next_pattern_tag()

        # Si no puso nombre le asignamos uno genérico
        if not name:
            name = f"Pattern_{tag}"

        new_pattern = LoadPattern(tag, name, factor)

        self.manager.add_pattern(new_pattern)
        self.load_patterns()

        # Selecionamos visualmente el último que acabamos de crear
        self.pattern_list.setCurrentRow(self.pattern_list.count() - 1)

    def update_pattern(self):
        selected = self.pattern_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecciona un pattern para actualizar.")
            return
        
        tag = selected[0].data(Qt.ItemDataRole.UserRole)
        pattern = self.manager.get_pattern(tag)

        if pattern:
            name = self.name_input.text().strip()
            pattern.name = name if name else pattern.name
            pattern.factor = self.factor_input.value()
            self.load_patterns()

    def delete_pattern(self):
        selected = self.pattern_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecciona un pattern para eleminar")
            return

        tag = selected[0].data(Qt.ItemDataRole.UserRole)
        pattern = self.manager.get_pattern(tag)

        if getattr(pattern, 'loads', []):
            reply = QMessageBox.question(
                self, 'Precaución de Dependencia',
                f"El patrón '{pattern.name}' tiene {len(pattern.loads)} fuerza(s) dentro.\nSi lo borras se destruirán también sus cargas.\n\n¿Deseas continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            # Rebotar si dice que No
            if reply == QMessageBox.StandardButton.No:
                return
        self.manager.delete_pattern(tag)
        self.load_patterns()
        self.name_input.clear()
        self.factor_input.setValue(1.0)
