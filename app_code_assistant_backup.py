import os
import streamlit as st
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from datetime import datetime
import json
from PIL import Image
from io import BytesIO
import base64
import html
import re

# ========== Setup Paths ==========
BASE_DIR = os.path.expanduser("~/myworkspace/utilities/code-demo")
FILES_DIR = os.path.join(BASE_DIR, "files")
os.makedirs(FILES_DIR, exist_ok=True)

# ========== Initialize Model ==========
llm = ChatOllama(model="codellama:7b-instruct")

# ========== Custom Styling ==========
def get_base_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, h3, h4, h5 {
        color: #2D2042;
    }

    .stButton > button {
        background-color: #60B5E5 !important;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
    }

    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5 {
        color: #60B5E5 !important;
    }

    section[data-testid="stFileUploader"] > div {
        box-shadow: 0px 1px 5px rgba(0, 0, 0, 0.05);
        border-radius: 8px;
        padding: 1rem;
    }

    #MainMenu {visibility: hidden;}
    /* footer {visibility: hidden;} */
    /* header {visibility: hidden;} */
    </style>
    """

# Apply the base styling
# Note: We've removed the wrapping toggle and related functions

# ========== Helper Functions ==========
def read_code_file(file):
    return file.read().decode("utf-8")

def build_prompt(task, code=None, user_prompt=None):
    if user_prompt:
        return f"{user_prompt}\n\n```python\n{code}\n```" if code else user_prompt
    elif task == "Explain":
        return f"Explain what this code does:\n\n```python\n{code}\n```"
    elif task == "Refactor":
        return f"""Please refactor the following code to improve clarity, maintainability, and performance. Provide only the revised code with inline comments and no additional explanation:

```python
{code}
```"""""
    elif task == "Debug":
        return f"Identify and fix bugs in the following code:\n\n```python\n{code}\n```"
    return ""

def save_output(input_data, result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(FILES_DIR, f"output_{timestamp}.json")
    with open(out_file, "w") as f:
        json.dump({"input": input_data, "response": result}, f, indent=2)

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ========== Streamlit UI ==========
# Logo and Title Header
logo_path = os.path.join(FILES_DIR, "logo.jpg")
if os.path.exists(logo_path):
    logo_base64 = get_base64_image(logo_path)
    st.markdown(
        f"""
        <div style='display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;'>
            <img src='data:image/png;base64,{logo_base64}' style='vertical-align: middle;' width='50'>
            <h1 style='margin: 0; font-family: Montserrat, sans-serif; color: #2D2042;'>Local Code Assistant with Codellama:7b-instruct</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.title("Local Code Assistant with Codellama:7b-instruct")

st.sidebar.header("✨ Interaction Mode ✨")
mode = st.sidebar.radio("Choose a mode:", ["Structured", "Direct Prompt"])
save_toggle = st.sidebar.checkbox("Save output to file", value=False)

# Initialize session state for response storage
if 'last_response' not in st.session_state:
    st.session_state.last_response = None

# Apply base styling
st.markdown(get_base_css(), unsafe_allow_html=True)

st.sidebar.markdown("---")
def_prompt = """
You are a helpful and concise code assistant. Your goal is to analyze user-submitted code and respond based on the task type.

- If explaining, be clear and beginner-friendly.
- If refactoring, improve readability and performance with brief justifications. Output the improved code directly.
- If debugging, explain the issues before showing the corrected version.

Respond using markdown formatting when appropriate. Only output code inside triple backticks.
"""
# --- Styled System Prompt Section ---
st.sidebar.markdown("""
    <div style='border: 1px solid #e6e6e6; padding: 12px; border-radius: 8px; background-color: #f9f9f9; margin-top: 10px; margin-bottom: 20px;'>
        <strong style='color: #2D2042;'>System Prompt</strong><br>
        <small style='color: #666;'>Customize how the model behaves. Use markdown-friendly formatting.</small>
    </div>
""", unsafe_allow_html=True)

custom_sys_prompt = st.sidebar.text_area("", value=def_prompt, height=180)

# --- Upload or paste code ---
uploaded_file = st.file_uploader("Upload a code file:", type=["py", "js", "java"])
code_input = st.text_area("Or paste your code here:")

code = ""
if uploaded_file:
    code = read_code_file(uploaded_file)
    st.success("Code loaded from uploaded file.")
elif code_input.strip():
    code = code_input

# --- Prompt Execution ---
if mode == "Structured":
    task = st.radio("What do you want to do?", ["Explain", "Refactor", "Debug"])
    if st.button("Run Analysis"):
        if not code:
            st.error("Please upload or enter some code.")
        else:
            with st.spinner("Generating model response..."):
                final_prompt = build_prompt(task, code)
                response = llm.invoke([
                    SystemMessage(content=custom_sys_prompt),
                    HumanMessage(content=final_prompt)
                ])
            
            # Store the response in session state for reuse
            st.session_state.last_response = response.content
            st.session_state.last_response_metadata = {
                "mode": mode, 
                "task": task, 
                "code": code
            }
            
            # Let the dynamic section at the bottom handle the display
            pass
            
            if save_toggle:
                save_output({"mode": mode, "task": task, "code": code}, response.content)
            

elif mode == "Direct Prompt":
    user_prompt = st.text_area("Enter your custom prompt:")
    if st.button("Run Prompt"):
        if not user_prompt.strip():
            st.error("Please enter a prompt.")
        else:
            with st.spinner("Generating model response..."):
                final_prompt = build_prompt(None, code if code else None, user_prompt)
                response = llm.invoke([HumanMessage(content=final_prompt)])
            
            # Store the response in session state for reuse
            st.session_state.last_response = response.content
            st.session_state.last_response_metadata = {
                "mode": mode,
                "prompt": user_prompt,
                "code": code
            }
            
            # Let the dynamic section at the bottom handle the display
            pass
            
            if save_toggle:
                save_output({"mode": mode, "prompt": user_prompt, "code": code}, response.content)
            

# Display the last response with scrollable view
if st.session_state.last_response is not None:
    st.markdown("---")
    
    # Display header
    st.subheader("Model Response")
    
    # Scrollable output with horizontal scrolling
    scrollable_output = f'''
    <div style="overflow-x: auto; width: 100%;">
        <pre style="
            background-color: #f6f6f6; 
            border-radius: 5px; 
            padding: 15px; 
            font-family: monospace; 
            border: 1px solid #e0e0e0;
            color: #333;
            white-space: pre;
            display: inline-block;
            min-width: 100%;
        ">{html.escape(st.session_state.last_response)}</pre>
    </div>
    '''
    st.markdown(scrollable_output, unsafe_allow_html=True)

# Footer Branding
st.markdown("""
    <hr style='margin-top: 3rem;'>
    <div style='text-align: center; color: #2D2042;'>Smarter Paths Forward</div>
""", unsafe_allow_html=True)


