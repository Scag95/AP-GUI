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
            # --- COMANDO: LABELS (ETIQUETAS) ---
            # Sintaxis: tag nodes on / tag elements off
            if verb == "tags" or verb == "tag":
                if len(args) < 2:
                    return "Uso: labels [nodes/elements] [on/off]", None
                
                target = args[0].lower() # nodes / elements
                state = args[1].lower()  # on / off
                
                is_visible = (state == "on")
                
                if target in ["node", "nodes"]:
                    # Devolvemos una ACCIÓN para que la UI la ejecute
                    return f"Etiquetas de Nodos: {state.upper()}", {"action": "toggle_node_labels", "value": is_visible}
                
                elif target in ["element", "elements"]:
                    return f"Etiquetas de Elementos: {state.upper()}", {"action": "toggle_element_labels", "value": is_visible}
                
                else:
                    return "Objetivo desconocido. Usa 'nodes' o 'elements'.", None
            
            # --- COMANDO: ANALYZE ---
            elif verb == "analyze":
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