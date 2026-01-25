# Arquitectura del Proyecto AP-GUI

Este documento describe el flujo de datos y dependencias del sistema actual. Utiliza diagramas Mermaid para visualizar las interacciones.

## 🏗️ Estructura General
El proyecto sigue una arquitectura **Model-View-Controller (adaptada)** donde:
- **Model (Análisis)**: Gestiona la lógica de negocio (Nodos, Elementos, OpenSees).
- **View (UI)**: Muestra la información y captura inputs.
- **Controller/Manager**: El `ProjectManager` centraliza el estado y comunica cambios.

```mermaid
graph TD
    %% Nodos Principales
    User((Usuario))
    Main[MainWindow]
    Manager["ProjectManager <br/> (Singleton)"]
    Viz["StructureInteractor <br/> (PyQtGraph)"]
    Props["PropertiesPanel <br/> (DockWidget)"]
    
    %% Subsistemas UI
    subgraph UI [src/ui]
        Menus[File/Define Menu]
        Dialogs[Wizard/Material Dialogs]
        Viz
        Props
    end
    
    %% Subsistemas Lógica
    subgraph Analysis [src/analysis]
        Nodes[Node Class]
        Elements[Element Class]
        Mats[Material Class]
        Secs[Section Class]
    end

    %% Relaciones
    User -->|Clics/Menús| UI
    
    %% Flujo de Comandos (Flechas Sólidas)
    Menus -->|1. Llamada| Manager
    Dialogs -->|1. Llamada| Manager
    Props -->|1. Modifica| Nodes
    
    %% Gestión de Datos
    Manager -->|Almacena| Nodes
    Manager -->|Almacena| Elements
    Manager -->|Almacena| Mats
    Manager -->|Almacena| Secs
    
    %% Flujo de Eventos (Flechas Punteadas)
    Manager -.->|2. Signal: dataChanged| Viz
    Viz -->|3. Lee Datos| Manager
    Viz -.->|Select| Props
    Props -.->|Signal: dataChanged| Main
    Main -.->|Refresh| Manager

    %% Dependencias
    Main --> Menus
    Main --> Viz
    Main --> Props
```

## 🧩 Mapa Detallado de Clases y Métodos
Detalle de las funciones implementadas hasta la fecha.

```mermaid
classDiagram
    %% --- CORE ---
    class ProjectManager {
        +instance() ProjectManager
        +dataChanged Signal
        %% Materiales/Secciones/Nodos/Elementos
        +get_all_nodes()
        +get_all_elements()
        +add_node(node)
        %% Persistencia
        +save_project(filename)
        +load_project(filename)
    }

    %% --- MODEL ---
    class Node {
        +int tag
        +float x
        +float y
    }

    class Element {
        +int tag
        +int node_i
        +int node_j
    }

    %% --- UI ---
    class MainWindow {
        +StructureInteractor viz_widget
        +PropertiesPanel props_panel
        +refresh_project()
    }

    class StructureInteractor {
        +refresh_viz()
        +_on_node_clicked()
        +nodeSelected Signal
        +selectionCleared Signal
    }
    
    class PropertiesPanel {
        +QStackedWidget stack
        +NodeForm node_form
        +show_node(node)
        +dataChanged Signal
    }

    class NodeForm {
        +load_node(node)
        +apply_changes()
        +dataChanged Signal
    }

    %% --- RELACIONES ---
    MainWindow *-- StructureInteractor
    MainWindow *-- PropertiesPanel
    PropertiesPanel *-- NodeForm
    StructureInteractor ..> PropertiesPanel : Connect (Select)
    PropertiesPanel ..> MainWindow : Connect (Changed)
```

## 🔄 Flujo de Selección y Edición
Como interactúan los componentes cuando el usuario edita un nodo:

1.  **Selección**:
    *   Usuario hace clic en un Nodo en `StructureInteractor`.
    *   `StructureInteractor` emite `nodeSelected(node)`.
    *   `PropertiesPanel` recibe la señal, muestra `NodeForm` y carga los datos (`x, y`).

2.  **Edición**:
    *   Usuario cambia `x` a `5.0` y pulsa "Aplicar".
    *   `NodeForm` actualiza el objeto `node.x = 5.0` directamente.
    *   `NodeForm` emite `dataChanged`.
    *   `PropertiesPanel` re-emite `dataChanged`.
    *   `MainWindow` recibe la señal y llama a `ProjectManager.instance().dataChanged.emit()`.
    *   `StructureInteractor` se entera del cambio y repinta todo (el nodo se mueve).
