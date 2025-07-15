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
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kalinga:wght@400;700&display=swap');
    :root {
        --primary-red: #a30000;
        --secondary-red: #c6323f;
        --light-gray: #f8f9fa;
        --dark-gray: #2c3e50;
        --border-gray: #dee2e6;
        --text-gray: #6c757d;
    }
    * { font-family: 'Kalinga', Arial, sans-serif !important; }
    .stDeployButton, header[data-testid="stHeader"] { display: none !important; }
    .stMainBlockContainer, .block-container, .main .block-container { padding: 0 !important; max-width: 100% !important; }
    .element-container:empty, .stMarkdown:empty { display: none !important; }
    .main-header {
        background-color: var(--primary-red); color: white; padding: 20px 30px; display: flex; justify-content: flex-start; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: fixed; top: 0; left: 0; right: 0; width: 100%; z-index: 999; box-sizing: border-box;
    }
    .header-left { display: flex; align-items: center; gap: 20px; }
    .logo-container { display: flex; align-items: center; gap: 15px; }
    .logo { height: 40px; width: auto; }
    .alexandria-title { font-size: 24px; font-weight: 700; color: white; font-family: 'Kalinga', Arial, sans-serif; }
    .agent-section { background-color: white; padding: 15px 30px; border-bottom: 1px solid var(--border-gray); display: flex; align-items: flex-start; justify-content: center; gap: 20px; position: fixed; top: 80px; left: 0; right: 0; width: 100%; z-index: 998; box-shadow: 0 2px 8px rgba(0,0,0,0.1); box-sizing: border-box; }
    .agent-content { display: flex; align-items: center; gap: 20px; max-width: 800px; }
    .agent-image { height: 80px; width: auto; flex-shrink: 0; object-fit: contain; }
    .agent-info { display: flex; flex-direction: column; align-items: flex-start; text-align: left; justify-content: flex-start; margin: 0; padding: 0; }
    .agent-title { font-size: 36px; font-weight: 700; color: var(--dark-gray); margin-bottom: 5px; margin-top: 0; padding: 0; font-family: 'Kalinga', Arial, sans-serif; line-height: 1.2; }
    .agent-subtitle { font-size: 18px; color: var(--text-gray); line-height: 1.2; font-family: 'Kalinga', Arial, sans-serif; margin: 0; padding: 0; }
    .conversation-container { min-height: 400px; max-height: calc(100vh - 300px); overflow-y: auto; padding: 20px; background-color: white; margin-top: 200px; margin-bottom: 20px; border: 1px solid var(--border-gray); border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .message { margin-bottom: 20px; padding: 0; clear: both; }
    .message.user { text-align: right; }
    .message.assistant { text-align: left; }
    .message-bubble-user { display: inline-block; max-width: 70%; padding: 15px 20px; border-radius: 20px; word-wrap: break-word; font-size: 14px; line-height: 1.4; position: relative; background-color: #a30000; color: white; margin-left: 30%; }
    .message-bubble-assistant { display: inline-block; max-width: 70%; padding: 15px 20px; border-radius: 20px; word-wrap: break-word; font-size: 14px; line-height: 1.4; position: relative; background-color: #f8f9fa; color: #2c3e50; margin-right: 30%; }
    .message-time { font-size: 12px; color: var(--text-gray); margin-top: 5px; }
    .welcome-prompt { text-align: center; padding: 60px 20px; color: var(--text-gray); }
    .welcome-text { font-size: 24px; font-weight: 300; margin-bottom: 10px; }
    .welcome-subtext { font-size: 16px; color: var(--text-gray); }
    .input-container-fixed { position: fixed; left: 0; right: 0; bottom: 0; width: 100vw; background: white; z-index: 1000; box-shadow: 0 -2px 10px rgba(0,0,0,0.08); padding: 20px 0 10px 0; }
    .input-form { max-width: 800px; margin: 0 auto; display: flex; gap: 10px; align-items: center; }
    .stTextInput input { border: 1px solid var(--border-gray) !important; border-radius: 25px !important; padding: 15px 20px !important; font-size: 16px !important; background-color: white !important; box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important; }
    .stTextInput input:focus { border-color: var(--primary-red) !important; box-shadow: 0 0 0 2px rgba(163, 0, 0, 0.2) !important; }
    .stButton button { background-color: var(--primary-red) !important; color: white !important; border: none !important; border-radius: 25px !important; padding: 15px 25px !important; font-weight: 600 !important; font-size: 16px !important; cursor: pointer !important; transition: all 0.3s ease !important; }
    .stButton button:hover { background-color: var(--secondary-red) !important; transform: translateY(-1px) !important; }
    @media (max-width: 768px) {
        .main-header { padding: 15px 20px; }
        .alexandria-title { font-size: 20px; }
        .agent-section { padding: 20px; top: 70px; }
        .agent-title { font-size: 24px; }
        .message-bubble-user, .message-bubble-assistant { max-width: 85%; }
        .input-container-fixed { padding: 10px 0 5px 0; }
        .conversation-container { max-height: calc(100vh - 250px); margin-top: 180px; }
    }
</style>
    ",
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