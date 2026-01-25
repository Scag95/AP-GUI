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
    
    %% Subsistemas UI
    subgraph UI [src/ui]
        Menus[File/Define Menu]
        Dialogs[Wizard/Material Dialogs]
        Viz
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
    
    %% Gestión de Datos
    Manager -->|Almacena| Nodes
    Manager -->|Almacena| Elements
    Manager -->|Almacena| Mats
    Manager -->|Almacena| Secs
    
    %% Flujo de Eventos (Flechas Punteadas)
    Manager -.->|2. Signal: dataChanged| Viz
    Viz -->|3. Lee Datos| Manager

    %% Dependencias
    Main --> Menus
    Main --> Viz
```

## 🧩 Mapa Detallado de Clases y Métodos
Detalle de las funciones implementadas hasta la fecha (Sesión de Persistencia).

```mermaid
classDiagram
    %% --- CORE ---
    class ProjectManager {
        +instance() ProjectManager
        +dataChanged Signal
        %% Materiales
        +add_material(mat)
        +get_material(tag)
        +get_all_materials()
        %% Secciones
        +add_section(sec)
        +get_section(tag)
        +get_all_sections()
        %% Nodos
        +add_node(node)
        +get_node(tag)
        +get_all_nodes()
        %% Elementos
        +add_element(ele)
        +get_element(tag)
        +get_all_elements()
        %% Persistencia
        +save_project(filename) bool
        +load_project(filename) bool
    }

    %% --- MODEL ---
    class Node {
        +int tag
        +float x
        +float y
        +to_dict() dict
        +from_dict(data) Node
    }

    class Element {
        +int tag
        +int node_i
        +int node_j
        +to_dict() dict
        +from_dict(data) Element
    }

    class ForceBeamColumn {
        +int section_tag
        +int transf_tag
        +get_opensees_command() str
    }

    Element <|-- ForceBeamColumn

    class FiberSection {
        +add_rect_patch()
        +add_layer_straight()
        +get_opensees_commands()
        +to_dict() dict
        +from_dict(data) FiberSection
    }

    class Concrete01 {
        +to_dict()
        +from_dict()
    }
    class Steel01 {
        +to_dict()
        +from_dict()
    }

    %% --- UI ---
    class MainWindow {
        +FileMenu file_menu
        +DefineMenu define_menu
        +StructureInteractor viz_widget
    }

    class StructureInteractor {
        +refresh_viz()
        +_on_node_clicked(plot, points)
    }
    
    class FileMenu {
        +open_save_dialog()
        +open_load_dialog()
    }
    
    class DefineMenu {
        +open_material_dialog()
        +open_section_dialog()
        +show_grid_dialog()
    }

    class FrameGenerator {
        +generate_2d_frame(stories, bays, ...)
    }

    %% --- RELACIONES ---
    MainWindow *-- StructureInteractor
    MainWindow *-- FileMenu
    MainWindow *-- DefineMenu
    DefineMenu ..> FrameGenerator : Usa
    StructureInteractor ..> ProjectManager : Escucha Señales
    FrameGenerator ..> ProjectManager : Añade Datos
```

## 🔄 Flujo de Datos Actual (Ej: Cargar Proyecto)

1.  **Usuario** hace clic en `Archivo > Cargar`.
2.  `FileMenu` abre diálogo y obtiene ruta del archivo.
3.  `FileMenu` llama a `ProjectManager.load_project(ruta)`.
4.  `ProjectManager` lee el JSON, instancia objetos (`Node`, `Element`, etc.) y los guarda.
5.  `ProjectManager` emite la señal **`dataChanged`**.
6.  `StructureInteractor` recibe la señal y ejecuta `refresh_viz()`.
7.  `StructureInteractor` pide la lista de nodos/elementos al `ProjectManager` y repinta la pantalla.

## 💾 Persistencia
Los objetos saben guardarse y cargarse a sí mismos mediante diccionarios:
- `to_dict()`: Objeto -> Diccionario (para JSON).
- `from_dict()`: Diccionario -> Objeto.

El `ProjectManager` orquesta esto iterando sobre sus listas.

## 🎨 Sistema de Selección (En Progreso)
```mermaid
sequenceDiagram
    participant User
    participant Plot as Interactor (ScatterPlot)
    participant Viz as StructureInteractor
    participant Mgr as ProjectManager

    User->>Plot: Clic en Nodo
    Plot->>Viz: Signal: sigClicked
    Viz->>Viz: Identifica nodo (p.data)
    Viz->>Viz: selected_node = nodo.tag
    Viz->>Viz: refresh_viz() (Pinta de rojo)
    Note over Viz: En el futuro, aquí pediremos<br/>datos extra al Manager
```
