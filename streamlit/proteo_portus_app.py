import streamlit as st
import base64
from datetime import datetime
import boto3
import json
import time

# ---------- CONFIGURACIÓN ----------
STEP_FUNCTION_ARN = (
    "arn:aws:states:eu-west-1:084375571972:stateMachine:Search_and_Evaluate_pipeline"
)
AWS_REGION = "eu-west-1"

# ---------- UTILIDADES ----------
def img_to_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


def call_step_function(prompt: str) -> str:
    client = boto3.client("stepfunctions", region_name=AWS_REGION)
    exec_arn = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        input=json.dumps({"prompt": prompt}),
    )["executionArn"]

    # Esperar a que termine
    while True:
        desc = client.describe_execution(executionArn=exec_arn)
        if desc["status"] in ("SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"):
            break
        time.sleep(1)

    if desc["status"] == "SUCCEEDED":
        out = json.loads(desc["output"])
        return (
            out.get("evaluation", {})
            .get("Payload", {})
            .get("llm_response", "Sin respuesta")
        )
    return f"⚠️ Error: {desc['status']}"


# ---------- CARGAR IMÁGENES ----------
logo_b64 = img_to_b64("logo-grupo-Typsa-1.png")
proteo_b64 = img_to_b64("imagenproteo.PNG")

# ---------- STREAMLIT SETUP ----------
st.set_page_config(
    page_title="ALEXANDRIA - Proteo Portus",
    page_icon=f"data:image/png;base64,{logo_b64}" if logo_b64 else "🔬",
    layout="wide",
)

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- CSS PERSONALIZADO ----------
with open(__file__, "r") as f:
    pass  # solo para evitar que el inspector quite el bloque largo de CSS
st.markdown(
    """
<!--  TODO: Pon aquí **integro** tu bloque CSS anterior.  
      Por brevedad lo omitimos en este snippet; copia & pega el que ya tenías.  -->
""",
    unsafe_allow_html=True,
)

# ---------- HEADER & AGENT ----------
st.markdown(
    f"""
<div class="main-header">
  <div class="header-left">
    <div class="logo-container">
      {'<img class="logo" src="data:image/png;base64,'+logo_b64+'"/>' if logo_b64 else ''}
      <div class="alexandria-title">ALEXANDRIA</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="agent-section">
   <div class="agent-content">
      {'<img class="agent-image" src="data:image/png;base64,'+proteo_b64+'"/>' if proteo_b64 else ''}
      <div class="agent-info">
          <div class="agent-title">Proteo Portus</div>
          <div class="agent-subtitle">
               Identifica y prepara referencias de proyectos que se alineen con los criterios de selección
          </div>
      </div>
   </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- PROCESAR ENVÍO ----------
def handle_send(user_msg: str):
    ts = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_msg, "timestamp": ts})

    with st.spinner("Pensando…"):
        try:
            bot_msg = call_step_function(user_msg)
        except Exception as e:
            bot_msg = f"⚠️ Error al invocar Step Functions: {e}"

    st.session_state.messages.append(
        {"role": "assistant", "content": bot_msg.replace("\n", "<br>"), "timestamp": ts}
    )


# ---------- FORMULARIO DE ENTRADA (barra fija abajo) ----------
with st.container():
    st.markdown(
        """
<div class="input-container-fixed">
  <div class="input-form">
""",
        unsafe_allow_html=True,
    )

    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        user_input = col1.text_input(
            label="Mensaje",
            placeholder="¿Cómo te puedo ayudar?",
            label_visibility="collapsed",
        )
        sent = col2.form_submit_button("Enviar")

    st.markdown("</div></div>", unsafe_allow_html=True)

    if sent and user_input.strip():
        handle_send(user_input)
        st.experimental_rerun()

# ---------- CONVERSACIÓN ----------
chat_html = '<div class="conversation-container" id="conversation-container">'
if st.session_state.messages:
    for m in st.session_state.messages:
        bubble = "message-bubble-user" if m["role"] == "user" else "message-bubble-assistant"
        chat_html += f"""
        <div class="message {m['role']}">
            <div class="{bubble}">{m['content']}</div>
            <div class="message-time">{m['timestamp']}</div>
        </div>
        """
else:
    chat_html += """
    <div class="welcome-prompt">
        <div class="welcome-text">¿Cómo te puedo ayudar?</div>
        <div class="welcome-subtext">Pregúntame sobre análisis de proyectos y criterios de selección</div>
    </div>
    """

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# Auto‑scroll al cargar
st.markdown(
    """
<script>
const chatBox = document.getElementById("conversation-container");
if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
</script>
""",
    unsafe_allow_html=True,
)
