
import streamlit as st
import base64
from datetime import datetime
import boto3
import json

# --- 1. CONSTANTS & CONFIGURATION ---
PAGE_TITLE = "ALEXANDRIA - Proteo Portus"
FAVICON_PATH = "logo-grupo-Typsa-1.png"
LOGO_PATH = "logo-grupo-Typsa-1.png"
PROTEO_IMAGE_PATH = "imagenproteo.PNG"
STEP_FUNCTION_ARN = "arn:aws:states:eu-west-1:084375571972:stateMachine:Search_and_Evaluate_pipeline"
AWS_REGION = "eu-west-1"

# --- 2. HELPER FUNCTIONS ---

def load_image_base64(file_path: str) -> str | None:
    """Loads an image from a file path and encodes it to base64."""
    try:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.warning(f"Image file not found: {file_path}")
        return None

def invoke_step_function(user_input: str):
    """Invokes the Step Function with the user's input."""
    try:
        client = boto3.client('stepfunctions', region_name=AWS_REGION)
        payload = {"mensaje": user_input}
        client.start_execution(
            stateMachineArn=STEP_FUNCTION_ARN,
            input=json.dumps(payload)  # Use json.dumps for safe serialization
        )
    except Exception as e:
        st.error(f"Error invoking Step Functions: {e}")

# --- 3. UI RENDERING FUNCTIONS ---

def render_custom_css():
    """Applies all custom CSS to the page."""
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
        .stDeployButton, header[data-testid="stHeader"] {
            display: none !important;
        }
        
        .stMainBlockContainer {
            padding: 0 !important;
        }
        
        /* Ocultar contenedores vacíos */
        .element-container:empty, .stMarkdown:empty {
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
            top: 80px; /* Height of main-header */
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
        }
        
        .agent-title {
            font-size: 36px;
            font-weight: 700;
            color: var(--dark-gray);
            margin-bottom: 5px;
            line-height: 1.2;
        }
        
        .agent-subtitle {
            font-size: 18px;
            color: var(--text-gray);
            line-height: 1.2;
        }
        
        /* Área de conversación */
        .conversation-container {
            min-height: 400px;
            max-height: calc(100vh - 300px);
            overflow-y: auto;
            padding: 20px;
            background-color: white;
            margin-top: 200px; /* Space for both fixed headers */
            margin-bottom: 20px;
            border: 1px solid var(--border-gray);
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .message {
            margin-bottom: 20px;
            clear: both;
        }
        
        .message.user { text-align: right; }
        .message.assistant { text-align: left; }
        
        .message-bubble {
            display: inline-block;
            max-width: 70%;
            padding: 15px 20px;
            border-radius: 20px;
            word-wrap: break-word;
            font-size: 14px;
            line-height: 1.4;
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
        
        .welcome-text { font-size: 24px; font-weight: 300; margin-bottom: 10px; }
        .welcome-subtext { font-size: 16px; }
        
        /* Input container */
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
            .main-header { padding: 15px 20px; }
            .alexandria-title { font-size: 20px; }
            .agent-section { padding: 10px 20px; top: 70px; }
            .agent-title { font-size: 24px; }
            .message-bubble { max-width: 85%; }
            .input-container { padding: 15px; }
            .conversation-container { max-height: calc(100vh - 250px); margin-top: 180px; }
        }
    </style>
    """, unsafe_allow_html=True)

def render_header(logo_b64_data: str | None):
    """Renders the main fixed header of the application."""
    logo_html = f'<img src="data:image/png;base64,{logo_b64_data}" class="logo" alt="TYPSA">' if logo_b64_data else ""
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

def render_agent_section(proteo_image_b64_data: str | None):
    """Renders the fixed agent information section."""
    proteo_image_html = f'<img src="data:image/png;base64,{proteo_image_b64_data}" class="agent-image" alt="Proteo">' if proteo_image_b64_data else '<div class="agent-image" style="background-color: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #a30000; height: 60px; width: 60px;">🔬</div>'
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

def render_conversation():
    """Renders the conversation area with all messages."""
    conversation_html = '<div class="conversation-container">'
    if st.session_state.messages:
        for message in st.session_state.messages:
            role = "user" if message["role"] == "user" else "assistant"
            # The original code forced assistant messages to "Gracias", so we keep that logic.
            content = message["content"] if role == "user" else "Gracias"
            conversation_html += f"""
            <div class="message {role}">
                <div class="message-bubble">{content}</div>
                <div class="message-time">{message["timestamp"]}</div>
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

# --- 4. MAIN APPLICATION LOGIC ---

def main():
    """Main function to run the Streamlit application."""
    # --- Page Configuration ---
    favicon_data = load_image_base64(FAVICON_PATH)
    favicon_html = f"data:image/png;base64,{favicon_data}" if favicon_data else "🔬"
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=favicon_html,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Load Assets ---
    logo_data = load_image_base64(LOGO_PATH)
    proteo_image_data = load_image_base64(PROTEO_IMAGE_PATH)

    # --- Initialize Session State ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = "Proteo Portus"

    # --- Render UI Components ---
    render_custom_css()
    render_header(logo_data)
    render_agent_section(proteo_image_data)
    render_conversation()

    # --- Chat Input Form ---
    st.markdown('<div class="input-container"><div class="input-form">', unsafe_allow_html=True)
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
    st.markdown('</div></div>', unsafe_allow_html=True)

    # --- Process Message ---
    if submit_button and user_input.strip():
        timestamp = datetime.now().strftime("%H:%M")
        
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Invoke Step Functions
        invoke_step_function(user_input)
        
        # Add bot response (simplified, as per original logic)
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Gracias",  # Original logic always showed "Gracias"
            "timestamp": timestamp
        })
        
        st.rerun()

if __name__ == "__main__":
    main()
