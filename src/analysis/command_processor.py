from src.analysis.manager import ProjectManager
from src.analysis.node import Node

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
            # --- OTROS COMANDOS ... ---
            else:
                return f"Comando desconocido: '{verb}'", None
        except Exception as e:
            return f"Error: {str(e)}", None       