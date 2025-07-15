import streamlit as st
import base64
from datetime import datetime
import boto3
import json

# Configuración de la página
# Cargar favicon
def load_favicon():
    try:
        with open('logo-grupo-Typsa-1.png', 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None
 
favicon_data = load_favicon()
favicon_html = f"data:image/png;base64,{favicon_data}" if favicon_data else "🔬"
 
st.set_page_config(
    page_title="ALEXANDRIA - Proteo Portus",
    page_icon=favicon_html,
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# Configuración de Step Functions
STEP_FUNCTION_ARN = "arn:aws:states:eu-west-1:084375571972:stateMachine:Search_and_Evaluate_pipeline"  # <-- Cambia esto
AWS_REGION = "eu-west-1"  # <-- Cambia esto si es necesario
 
# Cargar imágenes
def load_logo():
    try:
        with open('logo-grupo-Typsa-1.png', 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None
 
def load_proteo_image():
    try:
        with open('imagenproteo.PNG', 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None
 
logo_data = load_logo()
proteo_image_data = load_proteo_image()
 
# Inicializar session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_agent" not in st.session_state:
    st.session_state.current_agent = "Proteo Portus"
 
# CSS personalizado
 
st.markdown("""
<style>
    /* Importar fuente Kalinga */
    @import url('https://fonts.googleapis.com/css2?family=Kalinga:wght@400;700&display=swap');
   
    /* Variables globales */
    :root {
        --primary-red: #a30000;
        --secondary-red: #c6323f;
        --light-gray: #f8f9fa;
        --dark-gray: #2c3e50;
        --border-gray: #dee2e6;
        --text-gray: #6c757d;
    }
   
    /* Reset y configuración global */
    * {
        font-family: 'Kalinga', Arial, sans-serif !important;
    }
   
    /* Ocultar elementos de Streamlit */
    .stDeployButton {
        display: none !important;
    }
   
    header[data-testid="stHeader"] {
        display: none !important;
    }
   
    .stMainBlockContainer {
        padding: 0 !important;
    }
   
    /* Ocultar contenedores vacíos de Streamlit */
    .element-container:empty {
        display: none !important;
    }
   
    .stMarkdown:empty {
        display: none !important;
    }
   
    /* Eliminar márgenes y espaciado innecesario */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
   
    .main .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
   
   
    /* Banda roja fija en la parte superior */
    .main-header {
        background-color: var(--primary-red);
        color: white;
        padding: 20px 30px;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 999;
        box-sizing: border-box;
    }
   
    .header-left {
        display: flex;
        align-items: center;
        gap: 20px;
    }
   
    .logo-container {
        display: flex;
        align-items: center;
        gap: 15px;
    }
   
    .logo {
        height: 40px;
        width: auto;
    }
   
    .alexandria-title {
        font-size: 24px;
        font-weight: 700;
        color: white;
        font-family: 'Kalinga', Arial, sans-serif;
    }
   
    /* Título "Proteo Portus" fijo debajo de la banda roja */
    .agent-section {
        background-color: white;
        padding: 15px 30px;
        border-bottom: 1px solid var(--border-gray);
        display: flex;
        align-items: flex-start;
        justify-content: center;
        gap: 20px;
        position: fixed;
        top: 80px;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 998;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        box-sizing: border-box;
    }
   
    .agent-content {
        display: flex;
        align-items: center;
        gap: 20px;
        max-width: 800px;
    }
   
    .agent-image {
        height: 80px;
        width: auto;
        flex-shrink: 0;
        object-fit: contain;
    }
   
    .agent-info {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        text-align: left;
        justify-content: flex-start;
        margin: 0;
        padding: 0;
    }
   
    .agent-title {
        font-size: 36px;
        font-weight: 700;
        color: var(--dark-gray);
        margin-bottom: 5px;
        margin-top: 0;
        padding: 0;
        font-family: 'Kalinga', Arial, sans-serif;
        line-height: 1.2;
    }
   
    .agent-subtitle {
        font-size: 18px;
        color: var(--text-gray);
        line-height: 1.2;
        font-family: 'Kalinga', Arial, sans-serif;
        margin: 0;
        padding: 0;
    }
   
    /* Área de conversación - versión anterior */
    .conversation-container {
        min-height: 400px;
        max-height: calc(100vh - 300px);
        overflow-y: auto;
        padding: 20px;
        background-color: white;
        margin-top: 200px;
        margin-bottom: 20px;
        border: 1px solid var(--border-gray);
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
   
    .message {
        margin-bottom: 20px;
        padding: 0;
        clear: both;
    }
   
    .message.user {
        text-align: right;
    }
   
    .message.assistant {
        text-align: left;
    }
   
    .message-bubble {
        display: inline-block;
        max-width: 70%;
        padding: 15px 20px;
        border-radius: 20px;
        word-wrap: break-word;
        font-size: 14px;
        line-height: 1.4;
        position: relative;
    }
   
    .message.user .message-bubble {
        background-color: var(--primary-red);
        color: white;
        margin-left: 30%;
    }
   
    .message.assistant .message-bubble {
        background-color: var(--light-gray);
        color: var(--dark-gray);
        margin-right: 30%;
    }
   
    .message-time {
        font-size: 12px;
        color: var(--text-gray);
        margin-top: 5px;
    }
   
    /* Prompt inicial */
    .welcome-prompt {
        text-align: center;
        padding: 60px 20px;
        color: var(--text-gray);
    }
   
    .welcome-text {
        font-size: 24px;
        font-weight: 300;
        margin-bottom: 10px;
    }
   
    .welcome-subtext {
        font-size: 16px;
        color: var(--text-gray);
    }
   
    /* Input container - versión anterior visible */
    .input-container {
        background-color: white;
        border-top: 2px solid var(--border-gray);
        padding: 20px;
        box-shadow: 0 -4px 15px rgba(0,0,0,0.15);
        margin-top: 20px;
        position: relative;
        z-index: 100;
    }
   
   
    .input-form {
        max-width: 800px;
        margin: 0 auto;
        display: flex;
        gap: 10px;
        align-items: center;
    }
   
    /* Estilos para el input de Streamlit */
    .stTextInput input {
        border: 1px solid var(--border-gray) !important;
        border-radius: 25px !important;
        padding: 15px 20px !important;
        font-size: 16px !important;
        background-color: white !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
   
    .stTextInput input:focus {
        border-color: var(--primary-red) !important;
        box-shadow: 0 0 0 2px rgba(163, 0, 0, 0.2) !important;
    }
   
    .stButton button {
        background-color: var(--primary-red) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 15px 25px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
   
    .stButton button:hover {
        background-color: var(--secondary-red) !important;
        transform: translateY(-1px) !important;
    }
   
   
   
    /* Responsive */
    @media (max-width: 768px) {
        .main-header {
            padding: 15px 20px;
        }
       
        .alexandria-title {
            font-size: 20px;
        }
       
        .user-name {
            display: none;
        }
       
        .agent-section {
            padding: 20px;
        }
       
        .agent-title {
            font-size: 24px;
        }
       
        .message-bubble {
            max-width: 85%;
        }
       
        .input-container {
            padding: 15px;
        }
       
        .conversation-container {
            max-height: calc(100vh - 250px);
        }
       
        .agent-section {
            padding: 10px 20px;
            top: 70px;
        }
       
        .main-header {
            top: 0;
        }
       
        .conversation-container {
            max-height: calc(100vh - 250px);
            margin-top: 180px;
        }
       
        .input-container {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)
 
 
# Header principal - Logo y ALEXANDRIA a la izquierda
logo_html = f'<img src="data:image/png;base64,{logo_data}" class="logo" alt="TYPSA">' if logo_data else ""
 
st.markdown(f"""
<div class="main-header">
    <div class="header-left">
        <div class="logo-container">
            {logo_html}
            <div class="alexandria-title">ALEXANDRIA</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
 
# Sección del agente actual - Con imagen a la izquierda manteniendo proporciones
proteo_image_html = f'<img src="data:image/png;base64,{proteo_image_data}" class="agent-image" alt="Proteo">' if proteo_image_data else '<div class="agent-image" style="background-color: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #a30000; height: 60px; width: 60px;">🔬</div>'
 
# Sección del agente - fija en la parte superior
st.markdown(f"""
<div class="agent-section">
    <div class="agent-content">
        {proteo_image_html}
        <div class="agent-info">
            <div class="agent-title">Proteo Portus</div>
            <div class="agent-subtitle">Identifica y prepara referencias de proyectos que se alineen con los criterios de selección</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
 
# Área de conversación - contenedor fijo con scroll
conversation_html = '<div class="conversation-container">'
 
if st.session_state.messages:
    # Generar mensajes
    for message in st.session_state.messages:
        role = "user" if message["role"] == "user" else "assistant"
        content = message["content"]  
        conversation_html += f"""
        <div class="message {role}">
            <div class="message-bubble">
                {content}
            </div>
            <div class="message-time">{message["timestamp"]}</div>
        </div>
        """
else:
    # Mensaje de bienvenida
    conversation_html += """
    <div class="welcome-prompt">
        <div class="welcome-text">¿Cómo te puedo ayudar?</div>
        <div class="welcome-subtext">Pregúntame sobre análisis de proyectos y criterios de selección</div>
    </div>
    """
 
conversation_html += '</div>'
st.markdown(conversation_html, unsafe_allow_html=True)
 
# JavaScript para el toggle del sidebar
st.markdown("""
<script>
function toggleSidebar() {
    const sidebar = document.querySelector('.css-1d391kg');
    const body = document.body;
   
    if (sidebar.style.marginLeft === '-300px') {
        sidebar.style.marginLeft = '0';
        body.classList.remove('sidebar-collapsed');
    } else {
        sidebar.style.marginLeft = '-300px';
        body.classList.add('sidebar-collapsed');
    }
}
</script>
""", unsafe_allow_html=True)
 
# Función para generar respuestas
def generate_response(user_input):
    """Generar respuestas simples del asistente"""
    return "Gracias"
 
def invoke_step_function(user_input: str) -> str:
    client = boto3.client("stepfunctions", region_name=AWS_REGION)
    exec_arn = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        input=json.dumps({"mensaje": user_input}),
    )["executionArn"]

    # Espera (máx. 30 s) a que termine
    for _ in range(30):
        desc = client.describe_execution(executionArn=exec_arn)
        if desc["status"] == "SUCCEEDED":
            output = json.loads(desc["output"])
            return output["llm_response"]
        elif desc["status"] in ("FAILED", "TIMED_OUT", "ABORTED"):
            raise RuntimeError(f"Step Function terminó con estado {desc['status']}")
        time.sleep(1)

    raise TimeoutError("La ejecución tarda demasiado")
 
# Input en la parte inferior - no fijo
st.markdown("""
<div class="input-container">
    <div class="input-form">
""", unsafe_allow_html=True)
 
# Formulario de entrada
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
   
    with col1:
        user_input = st.text_input(
            "Mensaje",
            placeholder="¿Cómo te puedo ayudar?",
            label_visibility="collapsed",
            key="user_message"
        )
   
    with col2:
        submit_button = st.form_submit_button("Enviar")
 
st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)
 
# Procesar mensaje
if submit_button and user_input.strip():
    timestamp = datetime.now().strftime("%H:%M")
    # Agregar mensaje del usuario
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    # Invocar Step Functions
    try:
        invoke_step_function(user_input)
    except Exception as e:
        st.warning(f"Error al invocar Step Functions: {e}")
    # Generar respuesta
    try:
        bot_response = invoke_step_function(user_input)
    except Exception as e:
        bot_response = f"⚠️ Error: {e}"
    # Agregar respuesta del bot
    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_response,
        "timestamp": timestamp
    })
    st.rerun()