# AP-GUI — Análisis Estructural 2D con GUI para OpenSees

**AP-GUI** es una interfaz gráfica moderna e interactiva para el modelado, análisis y visualización estructural en 2D impulsada por **OpenSeesPy**.

---

## 🛠️ Tecnologías y Stack

- **GUI / Interfaz**: [PyQt6](https://riverbankcomputing.com/software/pyqt/)
- **Visualización 2D / Viewport**: [pyqtgraph](https://www.pyqtgraph.org/)
- **Motor de Cálculo Estructural**: [OpenSeesPy](https://openseespydoc.readthedocs.io/)
- **Lenguaje**: Python 3.10+

---

## 📁 Estructura del Repositorio

```text
AP-GUI/
├── docs/             # Documentación técnica, arquitectura e índice wiki
├── samples/          # Archivos de modelos de prueba en formato JSON
├── scripts/          # Scripts auxiliares y herramientas de desarrollo
├── tests/            # Batería de pruebas automatizadas (pytest y pytest-qt)
├── src/              # Código fuente principal de la aplicación
│   ├── analysis/     # Modelo de datos, gestor de proyecto y traductores OpenSees
│   ├── ui/           # Interfaz gráfica (ventanas, paneles, visualizadores, diálogos)
│   └── utils/        # Gestión de unidades, factores de escala y utilidades
├── main.py           # Punto de entrada principal de la aplicación
├── run_tests.py      # Lanzador unificado de la batería de pruebas
└── requirements.txt  # Dependencias del proyecto
```

---

## 🚀 Instalación y Uso

### 1. Entorno virtual

Se recomienda utilizar un entorno virtual de Python:

```bash
python -m venv venv
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux / macOS:
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```bash
python main.py
```

### 4. Ejecutar la batería de pruebas

Para verificar el funcionamiento del modelo y la aplicación mediante la suite de pruebas automatizadas:

```bash
python run_tests.py
# O directamente con pytest:
pytest
```

---

## 📚 Documentación

Para consultar la arquitectura detallada, el flujo de llamadas o las guías de contribución, revisa la carpeta [docs/](file:///c:/Users/alber/AP-GUI/docs):

- [Arquitectura e índice del proyecto](file:///c:/Users/alber/AP-GUI/docs/index.md)
- [Documento de Arquitectura Principal](file:///c:/Users/alber/AP-GUI/docs/ARCHITECTURE.md)
- [Esquema de datos JSON](file:///c:/Users/alber/AP-GUI/docs/schema.md)
- [Registro de cambios y desarrollo](file:///c:/Users/alber/AP-GUI/docs/log.md)
