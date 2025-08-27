import gradio as gr # type: ignore
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from smolagents import InferenceClientModel, Tool, CodeAgent # type: ignore

class GetLastOrderTool(Tool):
    name = "get_last_order"
    description = "Esta herramienta obtiene la lista de ingredientes del último pedido de supermercado del usuario."
    inputs = {}
    outputs = {"ingredients": {"type": "array", "description": "Lista de ingredientes del último pedido"}}
    output_type = "array"

    def forward(self):
        return ["tomates", "cebolla", "tortillas de maíz", "pollo", "queso", "aguacate"]


class RecipeFinderTool(Tool):
    name = "recipe_finder"
    description = "Busca recetas basadas en una cocina específica y una lista de ingredientes disponibles."
    inputs = {
        "cuisine": {"type": "string", "description": "Tipo de cocina, por ejemplo 'mexicana'"},
        "ingredients": {"type": "array", "description": "Lista de ingredientes disponibles"}
    }
    outputs = {"recipes": {"type": "string", "description": "Texto con las recetas encontradas"}}
    output_type = "string"

    def forward(self, cuisine: str, ingredients: list):
        recipes_db = {
    "mexicana": [
        {
            "name": "Tacos de Pollo",
            "required": ["tortillas de maíz", "pollo", "cebolla", "tomates"],
            "instructions": "1. Cocina el pollo en trozos pequeños hasta que esté dorado. 2. Pica finamente la cebolla y los tomates. 3. Calienta las tortillas de maíz. 4. Sirve el pollo en las tortillas y añade cebolla y tomate al gusto."
        },
        {
            "name": "Guacamole",
            "required": ["aguacate", "cebolla", "tomates"],
            "instructions": "1. Machaca 2-3 aguacates maduros en un bowl. 2. Pica finamente un poco de cebolla y tomate. 3. Mezcla todo junto. 4. Añade sal, pimienta y limón al gusto."
        },
        {
            "name": "Quesadillas",
            "required": ["tortillas de maíz", "queso"],
            "instructions": "1. Pon queso rallado en media tortilla de maíz. 2. Dobla la tortilla por la mitad. 3. Cocina en comal caliente por ambos lados hasta que el queso se derrita."
        }
    ],
    
    "colombiana": [
        {
            "name": "Pollo Guisado Costeño",
            "required": ["pollo", "cebolla", "tomates"],
            "instructions": "1. Sofríe la cebolla hasta que esté dorada. 2. Agrega el pollo en presas y dora por todos lados. 3. Incorpora los tomates picados y cocina hasta que se forme un guiso espeso. 4. Sazona con sal, comino y deja cocinar a fuego lento 25 minutos."
        },
        {
            "name": "Arepa Paisa Rellena",
            "required": ["tortillas de maíz", "pollo", "queso"],
            "instructions": "1. Calienta las tortillas de maíz en un comal. 2. Desmecha el pollo cocido y mezcla con un poco de queso. 3. Rellena las tortillas con la mezcla de pollo y queso. 4. Dobla como empanada y cocina hasta dorar."
        },
        {
            "name": "Guacamole Costeño",
            "required": ["aguacate", "cebolla", "tomates"],
            "instructions": "1. Machaca el aguacate muy bien. 2. Pica la cebolla y el tomate en cubitos muy pequeños. 3. Mezcla todo agregando sal y un toque de suero costeño (o sal). 4. Sirve fresco acompañando cualquier comida."
        }
    ],
    
    "argentina": [
        {
            "name": "Empanadas Criollas",
            "required": ["tortillas de maíz", "pollo", "cebolla"],
            "instructions": "1. Sofríe la cebolla cortada en juliana hasta que esté transparente. 2. Agrega el pollo desmenuzado y cocina 5 minutos. 3. Sazona con pimentón dulce, comino y sal. 4. Rellena las tortillas, dobla como empanada y cocina en sartén hasta dorar."
        },
        {
            "name": "Pollo a la Parrilla Porteño",
            "required": ["pollo", "tomates", "cebolla"],
            "instructions": "1. Marina el pollo con sal gruesa y orégano 30 minutos. 2. Cocina el pollo a la plancha hasta que esté bien dorado. 3. Prepara una salsa criolla con tomate y cebolla picados. 4. Sirve el pollo con la salsa criolla por encima."
        },
        {
            "name": "Provoleta Casera",
            "required": ["queso", "tomates", "cebolla"],
            "instructions": "1. Corta el queso en rebanadas gruesas. 2. Cocina en sartén hasta que esté dorado y derretido. 3. Pica tomate y cebolla finamente para hacer chimichurri simple. 4. Sirve el queso caliente con la mezcla de tomate y cebolla encima."
        }
    ],
    
    "española": [
        {
            "name": "Pollo al Chilindrón",
            "required": ["pollo", "tomates", "cebolla"],
            "instructions": "1. Sofríe la cebolla en aceite de oliva hasta que esté dorada. 2. Agrega el pollo troceado y dora bien. 3. Incorpora los tomates rallados y cocina hasta reducir. 4. Sazona con pimentón dulce, sal y cocina 20 minutos a fuego lento."
        },
        {
            "name": "Montadito de Aguacate",
            "required": ["tortillas de maíz", "aguacate", "tomates"],
            "instructions": "1. Tuesta ligeramente las tortillas de maíz. 2. Machaca el aguacate con un tenedor. 3. Unta el aguacate sobre las tortillas. 4. Corona con tomate picado muy fino y una pizca de sal marina."
        },
        {
            "name": "Tortilla de Queso Manchega",
            "required": ["queso", "cebolla"],
            "instructions": "1. Corta la cebolla en juliana fina y sofríe hasta caramelizar. 2. Ralla o corta el queso en láminas. 3. En una sartén, coloca capas de cebolla y queso. 4. Cocina a fuego lento hasta que el queso se derrita y forme una 'tortilla' dorada."
        }
    ]
}
        available_recipes = []
        if cuisine in recipes_db:
            for recipe in recipes_db[cuisine]:
                if all(item in ingredients for item in recipe["required"]):
                    available_recipes.append(f"### {recipe['name']}\n**Instrucciones:** {recipe['instructions']}\n")
        if not available_recipes:
            return "Lo siento, parece que con los ingredientes de tu último pedido no puedes preparar ninguna receta mexicana que yo conozca."
        return "\n".join(available_recipes)

SYSTEM_PROMPT = """
Eres un Chef Agente IA especializado ÚNICAMENTE en los ingredientes del último pedido del usuario.

REGLAS IMPORTANTES:
1. Para CUALQUIER pregunta sobre ingredientes, comida, recetas o cocina, SIEMPRE usa las herramientas.
2. NO respondas con tu conocimiento general sobre cocina.
3. SOLO usa la información que te den las herramientas.

Herramientas disponibles:
- get_last_order(): Para obtener ingredientes disponibles del último pedido
- recipe_finder(cuisine, ingredients): Para buscar recetas específicas con esos ingredientes

EJEMPLOS de cuándo usar herramientas:
- "¿Qué ingredientes tengo?" → Usar get_last_order()
- "¿Qué puedo cocinar?" → Usar get_last_order() y luego recipe_finder()
- "Dame una receta" → Usar get_last_order() y luego recipe_finder()
- "¿Cómo hago tacos?" → Usar get_last_order() y luego recipe_finder()

Si la pregunta NO es sobre comida/cocina (ej: "¿Cómo estás?"), puedes responder normalmente.
Pero para TODO lo relacionado con comida: USA LAS HERRAMIENTAS.
"""

model = InferenceClientModel(max_tokens=512, temperature=0.2)
agent = CodeAgent(
    model=model,
    tools=[GetLastOrderTool(), RecipeFinderTool()],
    stream_outputs=False,
    max_steps=3,
    verbosity_level=0,
)
agent.prompt_templates["system_prompt"] = SYSTEM_PROMPT

def extraer_respuesta_final_limpia(output_completo):
    """Extrae SOLO la respuesta final útil, eliminando TODO el debug"""
    if not output_completo:
        return "No se pudo generar respuesta."
    
    output_str = str(output_completo)
    
    # Dividir por líneas para análisis
    lines = output_str.split('\n')
    respuesta_limpia = []
    
    # Banderas para detectar secciones
    en_seccion_tecnica = False
    
    for line in lines:
        line_clean = line.strip()
        
        # Detectar inicio de secciones técnicas
        if any(pattern in line_clean for pattern in [
            '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
            'Step 1', 'Step 2', 'Step 3', 'Step 4',
            'Error in code parsing:',
            'Your code snippet is invalid',
            'Make sure to include code',
            'regex pattern',
            'Here is your code snippet:',
            'Executing parsed code:',
            'Duration', 'Input tokens', 'Output tokens',
            'Reached max steps',
            '─ Executing parsed code ─',
            'Out:', 'New run'
        ]):
            en_seccion_tecnica = True
            continue
        
        # Si estamos en sección técnica, saltar hasta encontrar contenido útil
        if en_seccion_tecnica:
            # Solo salir de sección técnica si encontramos contenido realmente útil
            if (line_clean and 
                not line_clean.startswith('─') and
                not line_clean.startswith('│') and
                not line_clean.startswith('╭') and
                not line_clean.startswith('╰') and
                not line_clean.startswith('[') and
                not '━━━' in line_clean and
                len(line_clean) > 20 and
                any(word in line_clean.lower() for word in ['receta', 'ingredientes', 'preparar', 'cocinar', 'instrucciones'])):
                en_seccion_tecnica = False
                respuesta_limpia.append(line_clean)
            continue
        
        # Si no estamos en sección técnica, conservar contenido útil
        if (line_clean and 
            not line_clean.startswith('─') and
            not line_clean.startswith('│') and
            len(line_clean) > 3):
            respuesta_limpia.append(line_clean)
    
    # Si encontramos respuesta limpia, devolverla
    if respuesta_limpia:
        return '\n'.join(respuesta_limpia)
    
    # Buscar texto entre "Out:" y errores
    if 'Out:' in output_str:
        parts = output_str.split('Out:')
        for part in parts[1:]:  # Saltar el primer part (antes del primer Out:)
            # Tomar hasta el siguiente marcador técnico
            clean_part = part.split('[Step')[0].split('Error in code')[0].strip()
            if len(clean_part) > 50 and ('receta' in clean_part.lower() or 'ingredientes' in clean_part.lower()):
                return clean_part
    
    # PASO 3: Último recurso - buscar cualquier texto útil largo
    for line in reversed(lines):
        line = line.strip()
        if (len(line) > 30 and 
            not any(skip in line for skip in ['Step', 'Error', 'regex', 'code', 'Duration', 'tokens']) and
            any(word in line.lower() for word in ['receta', 'ingredientes', 'preparar', 'cocinar'])):
            return line
    
    return "Disculpa, hubo un problema procesando la respuesta. ¿Puedes intentar de nuevo?"

def chef_chat_interface(message, mostrar_debug):
    """Interfaz principal con captura completa de salida"""
    try:
        if mostrar_debug:
            # Modo debug: mostrar todo tal como viene
            resultado = agent.run(message.strip(), reset=False)
            return f"**🔧 MODO DEBUG COMPLETO:**\n\n{resultado}"
        else:
            # Modo normal: capturar TODA la salida y limpiarla
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Capturar TODA la salida del agente
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                resultado = agent.run(message.strip(), reset=False)
            
            # Combinar todas las salidas
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()
            resultado_completo = f"{stdout_content}\n{stderr_content}\n{resultado}"
            
            # Extraer solo la respuesta final limpia
            respuesta_final = extraer_respuesta_final_limpia(resultado_completo)
            
            return respuesta_final
            
    except Exception as e:
        if mostrar_debug:
            return f"**🔧 ERROR DEBUG:**\n{str(e)}"
        else:
            return "Disculpa, hubo un problema. ¿Puedes reformular tu pregunta?"

# Crear interfaz con toggle de debug
with gr.Blocks(title="🧑‍🍳 Chef Agente IA") as demo:
    gr.Markdown("# 🧑‍🍳 Chef Agente IA 🥑")
    gr.Markdown("Chatea conmigo para descubrir qué recetas puedes preparar con tus compras del supermercado.")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(type="messages", height=400)
            msg = gr.Textbox(
                placeholder="Escribe tu pregunta sobre cocina aquí...",
                container=False
            )
        with gr.Column(scale=1):
            debug_toggle = gr.Checkbox(
                label="🔧 Modo Debug", 
                value=False, 
                info="Mostrar proceso interno del agente"
            )
    
    # Ejemplos
    gr.Examples(
        examples=[
            ["¿Qué ingredientes tengo disponibles?"],
            ["¿Qué comida mexicana puedo preparar con lo que compré?"],
            ["Dame una receta fácil con aguacate"],
            ["¿Qué recetas colombianas puedo hacer?"],
        ],
        inputs=[msg]
    )
    
    def respond(message, chat_history, debug_mode):
        # Obtener respuesta del agente
        bot_response = chef_chat_interface(message, chat_history, debug_mode)
        
        # Actualizar historial
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_response})
        
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot, debug_toggle], [msg, chatbot])

if __name__ == "__main__":
    demo.launch()
    
    # Fecha de nota actual: 22-08-2025
    # Ya estoy cansado... esta es la version 6...
    # Nota para mi mismo porque seguro lo olvido para mañana.
    # - No usar streaming, todo en una sola respuesta, los modelos gratis que encontre no lo osportan.
    # - No usar max_steps, porque no funciona bien con los modelos gratis solo unos pocos y esos los puedo usar poco.
    # - En caso no sea perfecto da igual, no sacamos la certificacion la idea es aprender.
    # - Luego de esto intentare con LangGraph
    