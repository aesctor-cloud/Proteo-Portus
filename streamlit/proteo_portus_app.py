import streamlit as st
import base64
from datetime import datetime
import boto3
import json
import time

# Configuración general
STEP_FUNCTION_ARN = "arn:aws:states:eu-west-1:084375571972:stateMachine:Search_and_Evaluate_pipeline"
AWS_REGION = "eu-west-1"

# Cargar imágenes
def load_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

logo_data = load_base64_image("logo-grupo-Typsa-1.png")
proteo_image_data = load_base64_image("imagenproteo.PNG")

favicon_html = f"data:image/png;base64,{logo_data}" if logo_data else "🔬"
st.set_page_config(
    page_title="ALEXANDRIA - Proteo Portus",
    page_icon=favicon_html,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# Estilos CSS + encabezado
st.markdown("""<style>/* CSS recortado para simplificar aquí. Usa el que me diste completo. */</style>""", unsafe_allow_html=True)

# Encabezado superior
st.markdown(f"""
<div class="main-header">
    <div class="header-left">
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_data}" class="logo">
            <div class="alexandria-title">ALEXANDRIA</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sección agente
agent_img = (
    f'<img src="data:image/png;base64,{proteo_image_data}" class="agent-image">'
    if proteo_image_data else "🔬"
)
st.markdown(f"""
<div class="agent-section">
    <div class="agent-content">
        {agent_img}
        <div class="agent-info">
            <div class="agent-title">Proteo Portus</div>
            <div class="agent-subtitle">Identifica y prepara referencias de proyectos que se alineen con los criterios de selección</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Contenedor de conversación
conversation_html = '<div class="conversation-container" id="conversation-container">'
if st.session_state.messages:
    for msg in st.session_state.messages:
        role = msg["role"]
        bubble_class = "message-bubble-user" if role == "user" else "message-bubble-assistant"
        conversation_html += f"""
        <div class="message {role}">
            <div class="{bubble_class}">{msg['content']}</div>
            <div class="message-time">{msg['timestamp']}</div>
        </div>
        """
else:
    conversation_html += """
    <div class="welcome-prompt">
        <div class="welcome-text">¿Cómo te puedo ayudar?</div>
        <div class="welcome-subtext">Pregúntame sobre análisis de proyectos y criterios de selección</div>
    </div>
    """
conversation_html += '</div>'
st.markdown(conversation_html, unsafe_allow_html=True)

# Input en la parte inferior
st.markdown("""
<style>
.input-container-fixed {
    position: fixed;
    left: 0; right: 0; bottom: 0;
    width: 100vw;
    background: white;
    z-index: 1000;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.08);
    padding: 20px 0 10px 0;
}
</style>
<div class="input-container-fixed"><div class="input-form">
""", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input("Mensaje", placeholder="¿Cómo te puedo ayudar?", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button("Enviar")

st.markdown("</div></div>", unsafe_allow_html=True)

# Lógica de Step Function
def invoke_step_function(prompt):
    client = boto3.client("stepfunctions", region_name=AWS_REGION)
    response = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        input=json.dumps({"prompt": prompt})
    )
    exec_arn = response["executionArn"]

    while True:
        result = client.describe_execution(executionArn=exec_arn)
        if result["status"] in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
            break
        time.sleep(1)

    if result["status"] == "SUCCEEDED":
        output = json.loads(result["output"])
        llm_response = output.get("evaluation", {}).get("Payload", {}).get("llm_response", "Sin respuesta")
        return llm_response.replace('\n', '<br>')
    else:
        return f"Error: {result['status']}"

# Envío de mensaje
if submit_button and user_input.strip():
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
    try:
        response = invoke_step_function(user_input)
    except Exception as e:
        response = f"Error al invocar Step Function: {str(e)}"
    st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
    st.rerun()
