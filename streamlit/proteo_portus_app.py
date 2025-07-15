import streamlit as st
import base64
from datetime import datetime
import boto3
import json
import time

# -- CONFIGURACIÓN --
STEP_FUNCTION_ARN = "arn:aws:states:eu-west-1:084375571972:stateMachine:Search_and_Evaluate_pipeline"
AWS_REGION = "eu-west-1"

# -- FUNCIONES --
def load_image_b64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

def invoke_step_function_and_get_response(user_input: str) -> str:
    client = boto3.client("stepfunctions", region_name=AWS_REGION)
    response = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        input=json.dumps({"prompt": user_input})
    )
    execution_arn = response["executionArn"]
    while True:
        desc = client.describe_execution(executionArn=execution_arn)
        if desc["status"] in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
            break
        time.sleep(1)
    if desc["status"] == "SUCCEEDED":
        output = json.loads(desc["output"])
        return output.get("evaluation", {}).get("Payload", {}).get("llm_response", "Sin respuesta")
    else:
        return f"⚠️ Error: Step Function terminó con estado {desc['status']}"

# -- CARGA IMÁGENES --
logo_data = load_image_b64("logo-grupo-Typsa-1.png")
proteo_data = load_image_b64("imagenproteo.PNG")

# -- CONFIG STREAMLIT --
favicon_data = logo_data
st.set_page_config(
    page_title="ALEXANDRIA - Proteo Portus",
    page_icon=favicon_data and f"data:image/png;base64,{favicon_data}",
    layout="wide"
)

# -- CSS PERSONALIZADO --
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
            font-family: 'Arial', sans-serif;
        }
        .title {
            text-align: center;
            margin-top: 40px;
        }
        .logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 400px;
        }
        .proteo-image {
            float: right;
            margin-top: 20px;
            width: 250px;
        }
        .chat-box {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 10px;
            max-height: 70vh;
            overflow-y: auto;
            margin-bottom: 100px;
        }
        .message-user {
            text-align: right;
            color: #a30000;
            margin-bottom: 10px;
        }
        .message-bot {
            text-align: left;
            color: #333333;
            margin-bottom: 10px;
        }
        .footer-form {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #ffffff;
            padding: 15px 30px;
            border-top: 1px solid #cccccc;
        }
    </style>
""", unsafe_allow_html=True)

# -- INICIALIZAR MENSAJES --
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# -- TÍTULO E IMÁGENES --
st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="logo">', unsafe_allow_html=True)
if proteo_data:
    st.markdown(f'<img src="data:image/png;base64,{proteo_data}" class="proteo-image">', unsafe_allow_html=True)

st.markdown("<h1 class='title'>ALEXANDRIA - Proteo Portus</h1>", unsafe_allow_html=True)

# -- CHAT BOX --
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    role_class = "message-user" if msg["role"] == "user" else "message-bot"
    st.markdown(f'<div class="{role_class}"><b>{msg["role"].capitalize()}:</b> {msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -- FORMULARIO FIJO ABAJO --
with st.form(key="chat_form", clear_on_submit=True):
    st.markdown('<div class="footer-form">', unsafe_allow_html=True)
    user_input = st.text_input("Escribe tu mensaje", "")
    send = st.form_submit_button("Enviar")
    st.markdown('</div>', unsafe_allow_html=True)

# -- PROCESAMIENTO AL ENVIAR --
if send and user_input:
    timestamp = datetime.now().strftime("%H:%M")
    # Añadir mensaje del usuario
    st.session_state["messages"].append({"role": "user", "content": user_input, "timestamp": timestamp})
    # Llamada a Step Function
    with st.spinner("Pensando..."):
        bot_response = invoke_step_function_and_get_response(user_input)
    # Añadir respuesta
    st.session_state["messages"].append({"role": "assistant", "content": bot_response, "timestamp": timestamp})
    # Recarga para mostrar mensajes nuevos
    st.rerun()
