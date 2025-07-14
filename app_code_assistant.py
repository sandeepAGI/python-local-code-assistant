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
import time
import requests
from typing import Optional

# ========== Setup Paths ==========
BASE_DIR = os.path.expanduser("~/myworkspace/utilities/code-demo")
FILES_DIR = os.path.join(BASE_DIR, "files")
os.makedirs(FILES_DIR, exist_ok=True)

# ========== Model Connection Error Handling ==========
def initialize_llm_with_retry(max_retries: int = 3, retry_delay: float = 2.0) -> Optional[ChatOllama]:
    """
    Initialize ChatOllama with robust error handling and retry logic.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Delay between retry attempts in seconds
        
    Returns:
        ChatOllama instance or None if connection fails
    """
    for attempt in range(max_retries):
        try:
            # Test if Ollama service is running
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code != 200:
                    raise ConnectionError("Ollama service not responding")
            except requests.exceptions.RequestException:
                raise ConnectionError("Cannot connect to Ollama service")
            
            # Initialize the model
            llm = ChatOllama(
                model="codellama:7b-instruct",
                temperature=0.1,
                top_p=0.9,
                num_ctx=4096
            )
            
            # Test the model with a simple query
            test_response = llm.invoke([
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Hello")
            ])
            
            if test_response and test_response.content:
                return llm
            else:
                raise ValueError("Model responded with empty content")
                
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Connection attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                st.error(f"Failed to initialize model after {max_retries} attempts: {str(e)}")
                st.error("Please ensure Ollama is running and the codellama:7b-instruct model is available.")
                return None
    
    return None

# ========== Initialize Model ==========
llm = initialize_llm_with_retry()

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
def validate_and_read_code_file(file) -> tuple[str, list[str]]:
    """
    Validate and read uploaded code file with comprehensive security checks.
    
    Args:
        file: Streamlit uploaded file object
        
    Returns:
        tuple: (file_content, list_of_warnings)
    """
    warnings = []
    
    # Check file size (max 1MB)
    MAX_FILE_SIZE = 1024 * 1024  # 1MB in bytes
    if file.size > MAX_FILE_SIZE:
        raise ValueError(f"File size ({file.size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)")
    
    # Read file content
    try:
        content = file.read().decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"File contains invalid UTF-8 characters: {str(e)}")
    
    # Check for potentially unsafe code patterns
    dangerous_patterns = [
        r'import\s+subprocess',
        r'import\s+os',
        r'exec\s*\(',
        r'eval\s*\(',
        r'__import__\s*\(',
        r'open\s*\(',
        r'file\s*\(',
        r'input\s*\(',
        r'raw_input\s*\(',
        r'compile\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
        r'vars\s*\(',
        r'dir\s*\(',
        r'getattr\s*\(',
        r'setattr\s*\(',
        r'hasattr\s*\(',
        r'delattr\s*\(',
    ]
    
    found_patterns = []
    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            found_patterns.append(pattern.replace(r'\s+', ' ').replace(r'\s*', '').replace(r'\(', '('))
    
    if found_patterns:
        warnings.append(f"Potentially unsafe code patterns detected: {', '.join(found_patterns)}")
    
    # Check for very long lines that might cause issues
    lines = content.split('\n')
    long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 500]
    if long_lines:
        warnings.append(f"Very long lines detected (>500 chars) at line numbers: {long_lines[:5]}")
    
    # Basic syntax validation for Python files
    if file.name.endswith('.py'):
        try:
            compile(content, file.name, 'exec')
        except SyntaxError as e:
            warnings.append(f"Python syntax error detected: {str(e)}")
    
    return content, warnings

def read_code_file(file):
    """Legacy function for backward compatibility"""
    content, warnings = validate_and_read_code_file(file)
    if warnings:
        for warning in warnings:
            st.warning(warning)
    return content

def safe_llm_invoke(llm_instance, messages, max_retries: int = 3, retry_delay: float = 1.0):
    """
    Safely invoke LLM with error handling and retry logic.
    
    Args:
        llm_instance: The ChatOllama instance
        messages: List of messages to send to the model
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retry attempts in seconds
        
    Returns:
        Model response or None if all attempts fail
    """
    if llm_instance is None:
        st.error("Model is not initialized. Please restart the application.")
        return None
        
    for attempt in range(max_retries):
        try:
            # Validate input messages
            if not messages or not isinstance(messages, list):
                raise ValueError("Messages must be a non-empty list")
            
            # Check for reasonable message sizes
            total_content_length = sum(len(msg.content) for msg in messages if hasattr(msg, 'content'))
            if total_content_length > 50000:  # ~50KB limit
                st.warning("Input is very large and may cause issues. Consider using smaller code snippets.")
            
            # Make the API call
            response = llm_instance.invoke(messages)
            
            # Validate response
            if not response or not hasattr(response, 'content') or not response.content:
                raise ValueError("Received empty response from model")
            
            # Check for common error patterns in response
            error_indicators = [
                "I cannot", "I can't", "I'm not able to", "I'm sorry, but",
                "Error:", "Exception:", "Traceback", "Failed to"
            ]
            
            response_text = response.content.lower()
            for indicator in error_indicators:
                if indicator.lower() in response_text[:200]:  # Check first 200 chars
                    st.warning(f"Model response may indicate an issue: {indicator}")
                    break
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                st.warning(f"Attempt {attempt + 1} failed: {error_msg}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                st.error(f"Failed to get response after {max_retries} attempts: {error_msg}")
                
                # Provide helpful error messages based on error type
                if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                    st.error("Connection issue: Please check if Ollama is running and accessible.")
                elif "context" in error_msg.lower() or "token" in error_msg.lower():
                    st.error("Input too large: Please try with a smaller code snippet.")
                elif "model" in error_msg.lower():
                    st.error("Model issue: Please ensure codellama:7b-instruct is properly installed.")
                
                return None
    
    return None

def estimate_token_count(text: str) -> int:
    """
    Estimate token count for input text (rough approximation).
    
    Args:
        text: Input text to estimate tokens for
        
    Returns:
        Estimated number of tokens
    """
    # Rough estimation: 1 token ≈ 4 characters for English text
    # This is a conservative estimate for code which may have more tokens
    return len(text) // 3

def validate_code_input(code: str, user_prompt: str = "") -> tuple[bool, list[str]]:
    """
    Validate code input for size, format, and potential issues.
    
    Args:
        code: Code string to validate
        user_prompt: Optional user prompt to include in validation
        
    Returns:
        tuple: (is_valid, list_of_warnings)
    """
    warnings = []
    
    # Check if input is empty
    if not code.strip() and not user_prompt.strip():
        return False, ["No code or prompt provided"]
    
    # Estimate token count
    total_text = code + user_prompt
    estimated_tokens = estimate_token_count(total_text)
    
    # Token limits based on model context window
    MAX_TOKENS = 3000  # Conservative limit for 4K context window
    WARN_TOKENS = 2000  # Warning threshold
    
    if estimated_tokens > MAX_TOKENS:
        return False, [f"Input too large: ~{estimated_tokens} tokens (max: {MAX_TOKENS}). Please use smaller code snippets."]
    elif estimated_tokens > WARN_TOKENS:
        warnings.append(f"Large input detected: ~{estimated_tokens} tokens. Consider using smaller code snippets for better results.")
    
    # Check for very long lines
    if code:
        lines = code.split('\n')
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 200]
        if len(long_lines) > 5:
            warnings.append(f"Many long lines detected (>200 chars). This may affect code analysis quality.")
    
    # Check for excessive repetition (potential copy-paste errors)
    if code:
        lines = code.split('\n')
        unique_lines = set(line.strip() for line in lines if line.strip())
        if len(lines) > 50 and len(unique_lines) < len(lines) * 0.5:
            warnings.append("High repetition detected in code. Please check for copy-paste errors.")
    
    # Basic Python syntax validation for code input
    if code.strip():
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            warnings.append(f"Python syntax error detected: {str(e)}")
    
    return True, warnings

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
                # Validate input before processing
                is_valid, validation_warnings = validate_code_input(code)
                
                if not is_valid:
                    for warning in validation_warnings:
                        st.error(warning)
                    st.stop()
                
                # Show warnings
                for warning in validation_warnings:
                    st.warning(warning)
                
                with st.spinner("Generating model response..."):
                    final_prompt = build_prompt(task, code) # Using new build_prompt
                    messages = [
                        SystemMessage(content=custom_sys_prompt), # Using potentially customized system prompt
                        HumanMessage(content=final_prompt)
                    ]
                    response = safe_llm_invoke(llm, messages)

                if response:
                    st.session_state.last_response = response.content
                    st.session_state.last_response_metadata = {
                        "mode": mode,
                        "task": task,
                        "code": code
                    }

                    if save_toggle:
                        save_output({"mode": mode, "task": task, "code": code}, response.content)
                else:
                    st.error("Failed to get response from model. Please try again.")


    elif mode == "Direct Prompt":
        user_prompt = st.text_area("Enter your custom prompt:", height=100)
        if st.button("Run Prompt", use_container_width=True):
            if not user_prompt.strip() and not code.strip():
                st.error("Please enter a prompt or provide some code.")
            else:
                # Validate input before processing
                is_valid, validation_warnings = validate_code_input(code if code else "", user_prompt)
                
                if not is_valid:
                    for warning in validation_warnings:
                        st.error(warning)
                    st.stop()
                
                # Show warnings
                for warning in validation_warnings:
                    st.warning(warning)
                
                with st.spinner("Generating model response..."):
                    final_prompt = build_prompt(None, code if code else None, user_prompt)
                    messages = [
                        SystemMessage(content=custom_sys_prompt), # Ensure system prompt is always used
                        HumanMessage(content=final_prompt)
                    ]
                    response = safe_llm_invoke(llm, messages)

                if response:
                    st.session_state.last_response = response.content
                    st.session_state.last_response_metadata = {
                        "mode": mode,
                        "prompt": user_prompt,
                        "code": code
                    }

                    if save_toggle:
                        save_output({"mode": mode, "prompt": user_prompt, "code": code}, response.content)
                else:
                    st.error("Failed to get response from model. Please try again.")

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