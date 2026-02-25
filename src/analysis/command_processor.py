from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QAction

from src.analysis.manager import ProjectManager
from src.analysis.node import Node
from src.analysis.opensees_translator import OpenSeesTranslator
from src.utils.units import UnitManager, UnitType


class CommandProcessor:
    def __init__(self):
        self.manager = ProjectManager.instance()

    def process_command(self, command_str):

        parts = command_str.split()
        if not parts:
            return ""

        verb = parts[0].lower()
        args = parts[1:]

        try:
            # --- COMANDO: ANALYZE ---
            if verb == "analyze":
                try:
                    translator = OpenSeesTranslator()
                    translator.build_model()
                    translator.run_gravity_analysis()
                    return "Análisis finalizado. Revisa la terminal para detalles.", None
                except Exception as e:
                    return f"Error en análisis: {str(e)}", None

            # --- COMANDO: CLEAR ---
            elif verb == "clear":
                return "Consola limpiada", {"action": "clear_console"}

            # --- COMANDO: SCALE ---
            elif verb == "scale":
                if len(args) < 2:
                    return "Uso: scale [load|deformation|moment|shear] [valor]", None
                
                s_type = args[0].lower()
                
                # Mapeo de alias para scale
                if s_type in ['node', 'nodes']: s_type = 'node_size'
                elif s_type in ['deformed', 'def']: s_type = 'deformation'
                elif s_type in ['moments', 'm']: s_type = 'moment'
                elif s_type in ['shear', 'v']: s_type = 'shear'

                try:
                    val = float(args[1])
                    from src.utils.scale_manager import ScaleManager # Import local para evitar ciclos si los hubiera
                    ScaleManager.instance().set_user_multiplier(s_type, val)
                    return f"Multiplicador de escala '{s_type}' establecido a {val}x", None
                except ValueError:
                    return "Error: El valor debe ser numérico", None

            # --- COMANDO: SHOW / HIDE (Visibilidad) ---
            elif verb == "show" or verb == "hide":
                if not args:
                    return "Uso: [show/hide] [loads/deformed/diagrams] [sub-arg]", None
                
                arg = args[0].lower()
                is_show = (verb == "show")

                # Caso Especial: DIAGRAMS [Tipo]
                if arg in ["diagrams", "diagram", "forces"]:
                    if len(args) > 1:
                        dtype = args[1].upper()
                        if dtype in ['M', 'V', 'P', 'S']:
                            if dtype == 'S': dtype = 'V' # Alias
                            if is_show:
                                return f"Diagrama '{dtype}' activado", {"action": "set_diagram_type", "value": dtype}
                    
                    # Si no hay sub-arg, toggle general
                    return f"Visibilidad Diagramas: {is_show}", {"action": "set_visibility", "type": "diagrams", "value": is_show}

                # Caso Especial: LOADS [N/E]
                if arg in ["loads", "load"]:
                    if len(args) > 1:
                        sub = args[1].lower()
                        if sub in ['n', 'node', 'nodes']:
                             return f"Cargas Nodos: {is_show}", {"action": "set_load_visibility", "type": "nodes", "value": is_show}
                        elif sub in ['e', 'element', 'elements']:
                             return f"Cargas Elementos: {is_show}", {"action": "set_load_visibility", "type": "elements", "value": is_show}
                    
                    # General
                    return f"Visibilidad Cargas: {is_show}", {"action": "set_visibility", "type": "loads", "value": is_show}

                # Resto de casos generales
                target_map = {
                    "deformed": "deformed", "deformation": "deformed",
                    "nodes": "node_labels", "node": "node_labels",
                    "elements": "element_labels", "element": "element_labels"
                }
                
                if arg in target_map:
                    target = target_map[arg]
                    # Mapeo de acciones específicas
                    if target == "node_labels":
                        return f"Etiquetas Nodos: {is_show}", {"action": "toggle_node_labels", "value": is_show}
                    elif target == "element_labels":
                        return f"Etiquetas Elementos: {is_show}", {"action": "toggle_element_labels", "value": is_show}
                    else:
                        return f"Visibilidad de '{target}': {is_show}", {"action": "set_visibility", "type": target, "value": is_show}
                else:
                    return "Objetivo desconocido.", None

            # --- COMANDO: REGEN ---
            elif verb == "regen":
                from src.utils.scale_manager import ScaleManager
                ScaleManager.instance().autocalculate_scales()
                return "Escalas regeneradas automáticamente.", None

            # --- COMANDO: UNITS ---
            elif verb == "units":
                if not args:
                    return "Uso: units [m|cm|mm|ft|in]", None
                
                unit_name = args[0]
                manager = UnitManager.instance()
                # Cambiamos solo la longitud para probar
                manager.set_unit(UnitType.LENGTH, unit_name)
                return f"Unidad de longitud cambiada a: {unit_name}", None # {"action": "refresh_ui"} si fuera necesario

            elif verb == "check":
                try:
                    # Creamos traductor solo para volcar el modelo (asumiendo que ya se hizo analyze antes, 
                    # pero ojo: opensees es stateful global. Si ya corriste analyze, el modelo sigue vivo).
                    # Si no, esto crearía uno nuevo. 
                    
                    # MEJOR ESTRATEGIA: Como la instancia de ops es global, 
                    # simplemente llamamos a printModel directamente o a través del traductor.
                    
                    translator = OpenSeesTranslator()
                    # Si no hay modelo, construimos uno rápido para ver qué sale
                    # Pero lo ideal es usarlo después de analyze.
                    # Asumiremos que el usuario hace 'analyze' primero, o que el translator lo construye.
                    
                    # Opción segura: Construir y volcar.
                    translator.build_model()
                    translator.dump_model_to_file("debug_model.out")
                    return "Modelo volcado a 'debug_model.out'. Revisa ese archivo.", None
                except Exception as e:
                    return f"Error en check: {str(e)}", None
            
            elif verb == "exit":
                QApplication.instance().quit()
                return "Cerrando aplicación...", None
            
            else:
                return f"Comando desconocido: '{verb}'", None
        except Exception as e:
            return f"Error: {str(e)}", None       