import streamlit as st
import base64
from datetime import datetime
import boto3
import json
import time

# -- CONFIGURACIÓN STEP FUNCTIONS --
STEP_FUNCTION_ARN = "arn:aws:states:eu-west-1:084375571972:stateMachine:Search_and_Evaluate_pipeline"
AWS_REGION = "eu-west-1"


# -- UTILIDADES --
def load_image_b64(path):
    try:
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

def invoke_step_function_and_get_response(user_input: str) -> str:
    client = boto3.client('stepfunctions', region_name=AWS_REGION)
    response = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        input=json.dumps({"prompt": user_input})
    )
    exec_arn = response["executionArn"]
    while True:
        desc = client.describe_execution(executionArn=exec_arn)
        status = desc["status"]
        if status in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
            break
        time.sleep(1)
    if status == "SUCCEEDED":
        output = json.loads(desc["output"])
        # Ajusta la navegación por JSON según tu output real
        llm_response = output.get("evaluation", {}) \
                             .get("Payload", {}) \
                             .get("llm_response", "Sin respuesta")
        return llm_response
    else:
        return f"⚠️ Error: Step Function terminó con estado {status}"


# -- STREAMLIT LAYOUT & ESTILO --
favicon_data = load_image_b64('logo-grupo-Typsa-1.png')
st.set_page_config(page_title="ALEXANDRIA - Proteo Portus",
                   page_icon=favicon_data and f"data:image/png;base64,{favicon_data}",
                   layout="wide")

logo_data = load_image_b64('logo-grupo-Typsa-1.png')
proteo_data = load_image_b64('imagenproteo.PNG')

# Inicializar session state
st.session_state.setdefault("messages", [])

# Estilos básicos
st.markdown("""
<style>
.conversation-container { padding:20px; border:1px solid #dee2e6; border-radius:8px; max-height:70vh; overflow-y:auto; margin-top:120px; }
.message-bubble-user {background:#a30000;color:white;padding:10px 15px;border-radius:20px;max-width:70%; margin-left:30%;}
.message-bubble-assistant {background:#f8f9fa;color:#2c3e50;padding:10px 15px;border-radius:20px;max-width:70%; margin-right:30%;}
.message-time {font-size:12px;color:#6c757d;margin-top:4px;}
.input-container {position:fixed;bottom:0;width:100%;padding:15px;background:white;border-top:1px solid #dee2e6;}
.input-form {display:flex;gap:10px;}
</style>
""", unsafe_allow_html=True)

# Header fijo
st.markdown(f"""
<div style="position:fixed;top:0;left:0;right:0;background:#a30000;color:white;padding:15px;z-index:999;">
    <img src="data:image/png;base64,{logo_data}" height="30"/> ALEXANDRIA
</div>
""", unsafe_allow_html=True)

# Área conversación
st.markdown('<div class="conversation-container" id="chat">', unsafe_allow_html=True)
for m in st.session_state.messages:
    bubble = "message-bubble-user" if m["role"] == "user" else "message-bubble-assistant"
    st.markdown(f'''
        <div class="message {m["role"]}">
          <div class="{bubble}">{m["content"]}</div>
          <div class="message-time">{m["timestamp"]}</div>
        </div>
    ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Formulario input fijo abajo
st.markdown('<div class="input-container"><form class="input-form">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Tu mensaje", key="user_message")
    send = st.form_submit_button("Enviar")
st.markdown('</form></div>', unsafe_allow_html=True)

# -- LÓGICA DE ENVÍO Y RESPUESTA --
if send and user_input:
    timestamp = datetime.now().strftime("%H:%M")
    # Añadir mensaje de usuario
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
    # Obtener respuesta del bot
    with st.spinner("Pensando…"):
        bot_response = invoke_step_function_and_get_response(user_input)
    # Añadir mensaje del bot
    st.session_state.messages.append({"role": "assistant", "content": bot_response, "timestamp": timestamp})
    st.experimental_rerun()
