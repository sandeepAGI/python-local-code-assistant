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

# ========== Helper Functions ==========
def read_code_file(file):
    return file.read().decode("utf-8")

# --- ENHANCED build_prompt function (No Multi-line Strings) ---
def build_prompt(task, code=None, user_prompt=None, refactor_focus_areas=None):
    """
    Builds the prompt for the LLM based on the selected task or direct input.
    Uses enhanced, structured prompts for Explain, Refactor, and Debug.
    """
    if user_prompt:  # Direct Prompt mode
        # The SystemMessage will be added separately when invoking the LLM
        return f"{user_prompt}\n\n```python\n{code}\n```" if code else user_prompt

    elif task == "Explain":
        prompt = "Explain the following Python code:\n\n"
        prompt += "```python\n"
        prompt += code
        prompt += "\n```"
        return prompt

    elif task == "Refactor":
        # Provides default focus areas if none are specified.
        if refactor_focus_areas is None:
            refactor_focus_areas = ["clarity", "maintainability", "performance"]
        focus_str = ", ".join(refactor_focus_areas)

        prompt = f"Please refactor the following Python code. Your primary goals are to improve: {focus_str}.\n"
        prompt += "First, provide an explanation of the changes made and why they improve the code.\n"
        prompt += "Then, provide the complete, revised Python code block with concise inline comments (#) for significant changes.\n\n"
        prompt += "Original Code:\n"
        prompt += "```python\n"
        prompt += code
        prompt += "\n```\n\n"
        prompt += "Explanation and Refactored Code:\n" # New guide
        return prompt

    elif task == "Debug":
        prompt = "Analyze and debug the following Python code:\n\n"
        prompt += "```python\n"
        prompt += code
        prompt += "\n```"
        return prompt
        
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
st.set_page_config(layout="wide") # Use wide layout for better code display

# Logo and Title Header
logo_path = os.path.join(FILES_DIR, "logo.jpg")
if os.path.exists(logo_path):
    try:
        logo_base64 = get_base64_image(logo_path)
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;'>
                <img src='data:image/jpeg;base64,{logo_base64}' style='vertical-align: middle;' width='50'>
                <h1 style='margin: 0; font-family: Montserrat, sans-serif; color: #2D2042;'>Local Python Code Assistant with Codellama:7b-instruct</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.warning(f"Could not load logo: {e}")
        st.title("Local Python Code Assistant with Codellama:7b-instruct")
else:
    st.title("Local Python Code Assistant with Codellama:7b-instruct")


st.sidebar.header("✨ Interaction Mode ✨")
mode = st.sidebar.radio("Choose a mode:", ["Structured", "Direct Prompt"])
save_toggle = st.sidebar.checkbox("Save output to file", value=False)

# Initialize session state for response storage
if 'last_response' not in st.session_state:
    st.session_state.last_response = None
if 'last_response_metadata' not in st.session_state:
    st.session_state.last_response_metadata = {}


# Apply base styling
st.markdown(get_base_css(), unsafe_allow_html=True)

st.sidebar.markdown("---")

# --- ENHANCED System Prompt ---
new_def_prompt = """
You are a helpful and concise AI code assistant. Your primary goal is to analyze user-submitted Python code and respond accurately and effectively based on the specified task.

- **Explaining Code**:
  Provide a clear and beginner-friendly explanation. Your explanation should cover:
  1. The overall purpose and functionality of the code.
  2. A breakdown of key components (functions, classes, significant logic blocks).
  3. The expected input(s) and output(s).
  4. Any potential edge cases or notable behaviors you observe.
  Be thorough yet concise.

- **Refactoring Code**:
  Your goal is to improve the code based on specified focus areas (e.g., clarity, maintainability, performance, Pythonic idioms).
  Please provide:
  1. A clear explanation of the changes you made and the reasoning behind them.
  2. The complete, revised Python code block.
  3. Ensure the code block includes concise inline comments (`#`) for significant changes.
  Ensure the refactored code remains functionally equivalent to the original.

- **Debugging Code**:
  Analyze the code for bugs, errors, and potential issues. Present your findings in a structured manner:
  1.  **Bug Identification**: Clearly list each bug or issue found. Explain *why* it is an issue (e.g., syntax error, logical flaw, runtime risk, deviation from best practices).
  2.  **Proposed Fixes**: For each identified bug, describe the necessary changes to correct it.
  3.  **Corrected Code**: Provide the complete Python code block with all identified bugs fixed.

Always use Markdown for formatting your response. Code blocks must be enclosed in triple backticks (```python ... ```).
"""

# --- Styled System Prompt Section ---
st.sidebar.markdown("""
    <div style='border: 1px solid #e6e6e6; padding: 12px; border-radius: 8px; background-color: #f9f9f9; margin-top: 10px; margin-bottom: 20px;'>
        <strong style='color: #2D2042;'>System Prompt</strong><br>
        <small style='color: #666;'>Customize how the model behaves. Use markdown-friendly formatting.</small>
    </div>
""", unsafe_allow_html=True)

# Use the new prompt as the default
custom_sys_prompt = st.sidebar.text_area("", value=new_def_prompt, height=350) # Increased height

# --- Main Area Layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Code")
    # --- Upload or paste code ---
    uploaded_file = st.file_uploader("Upload a code file:", type=["py", "js", "java"])
    code_input = st.text_area("Or paste your code here:", height=300)

    code = ""
    if uploaded_file:
        code = read_code_file(uploaded_file)
        # Display the loaded code
        st.code(code, language='python') # Show uploaded code
    elif code_input.strip():
        code = code_input

    # --- Prompt Execution ---
    st.subheader("Controls")
    if mode == "Structured":
        task = st.radio("What do you want to do?", ["Explain", "Refactor", "Debug"])
        # Future enhancement: Add checkboxes here for refactor_focus_areas
        if st.button("Run Analysis", use_container_width=True):
            if not code:
                st.error("Please upload or enter some code.")
            else:
                with st.spinner("Generating model response..."):
                    final_prompt = build_prompt(task, code) # Using new build_prompt
                    response = llm.invoke([
                        SystemMessage(content=custom_sys_prompt), # Using potentially customized system prompt
                        HumanMessage(content=final_prompt)
                    ])

                st.session_state.last_response = response.content
                st.session_state.last_response_metadata = {
                    "mode": mode,
                    "task": task,
                    "code": code
                }

                if save_toggle:
                    save_output({"mode": mode, "task": task, "code": code}, response.content)


    elif mode == "Direct Prompt":
        user_prompt = st.text_area("Enter your custom prompt:", height=100)
        if st.button("Run Prompt", use_container_width=True):
            if not user_prompt.strip() and not code.strip():
                st.error("Please enter a prompt or provide some code.")
            else:
                with st.spinner("Generating model response..."):
                    final_prompt = build_prompt(None, code if code else None, user_prompt)
                    # --- MODIFIED llm.invoke to include SystemMessage ---
                    response = llm.invoke([
                        SystemMessage(content=custom_sys_prompt), # Ensure system prompt is always used
                        HumanMessage(content=final_prompt)
                    ])

                st.session_state.last_response = response.content
                st.session_state.last_response_metadata = {
                    "mode": mode,
                    "prompt": user_prompt,
                    "code": code
                }

                if save_toggle:
                    save_output({"mode": mode, "prompt": user_prompt, "code": code}, response.content)

with col2:
    st.subheader("Model Response")
    # Display the last response with scrollable view
    if st.session_state.last_response is not None:
        # Use st.markdown for rich text rendering including code blocks
        st.markdown(st.session_state.last_response, unsafe_allow_html=True)
    else:
        st.info("The model's response will appear here.")


# Footer Branding - placed at the bottom, outside columns
st.markdown("""
    <hr style='margin-top: 3rem;'>
    <div style='text-align: center; color: #2D2042;'>Smarter Paths Forward</div>
""", unsafe_allow_html=True)