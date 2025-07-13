# Local Code Assistant with Codellama & Streamlit

This project provides a simple yet powerful Streamlit web application that acts as a local code assistant, leveraging the `codellama:7b-instruct` model through Ollama and LangChain. It allows users to explain, refactor, and debug Python code snippets, or interact with the model using direct prompts.

## Description

The application offers a user-friendly interface to interact with a locally running large language model (LLM) specifically trained for code-related tasks. It aims to showcase how LLMs can be integrated into development workflows for tasks like code comprehension, improvement, and troubleshooting. The project also serves as a case study in iterative prompt engineering to achieve desired outputs from the LLM.

**Core Technologies:**

* **LLM:** `codellama:7b-instruct` (via Ollama)
* **Framework:** Streamlit
* **LLM Orchestration:** LangChain (`langchain-ollama`)

## Features

* **Code Input:** Upload Python files or paste code directly into a text area.
* **Interaction Modes:**
    * **Structured Mode:** Choose from predefined tasks:
        * **Explain:** Get a detailed, beginner-friendly explanation of the code, including purpose, components, I/O, and edge cases.
        * **Refactor:** Receive a refactored version of the code *along with* an explanation of the changes made to improve clarity, maintainability, or performance.
        * **Debug:** Get a structured report identifying bugs, proposing fixes, and providing the corrected code.
    * **Direct Prompt Mode:** Interact freely with the model, optionally providing code as context.
* **Custom System Prompt:** Modify the underlying system prompt in the sidebar to experiment with model behavior.
* **Output Display:** View the model's response in a clear, Markdown-formatted display.
* **Save Output:** Optionally save interactions (input & response) to JSON files.

## Setup & Installation

### Prerequisites

* **Python 3.8+**: Ensure you have a compatible Python version installed.
* **Ollama**: You must have Ollama installed and running. You can download it from [ollama.com](https://ollama.com/).
* **Git (Optional):** For cloning the repository.

### Installation

1.  **Clone the Repository (Optional):**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```
2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:** Create a `requirements.txt` file with the following content (or add as needed):
    ```txt
    streamlit
    langchain-ollama
    langchain
    numpy
    scipy
    pandas
    selenium
    webdriver-manager
    # Add any other libraries your demo snippets might use
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

### Ollama Setup

1.  **Ensure Ollama is Running:** Start the Ollama application or service.
2.  **Pull the Model:** If you haven't already, pull the `codellama:7b-instruct` model:
    ```bash
    ollama pull codellama:7b-instruct
    ```

### Project Structure

Ensure you have a `files` directory in your project root. If you want to use a logo, place it as `logo.jpg` inside the `files` directory.

```
your-project/
├── app_code_assistant.py
├── files/
│   └── logo.jpg  (Optional)
├── README.md
└── requirements.txt
```

## Usage

1.  Navigate to your project directory in the terminal.
2.  Ensure your virtual environment is active.
3.  Ensure Ollama is running.
4.  Run the Streamlit application:
    ```bash
    streamlit run app_code_assistant.py
    ```
5.  Open your web browser to the local address provided by Streamlit.
6.  Use the sidebar to select the mode, upload/paste code, and interact with the assistant.

## Limitations & Considerations

It's important to understand the limitations when working with a 7B/8B parameter model locally:

* **Context Window:** These models have a finite "context window" (the amount of text they can consider at once, both input and output). While Codellama can support large windows in theory, practical local implementations often have limits. As we observed during testing, providing very large code snippets (like the entire application script) can exceed this limit, leading to:
    * The model "forgetting" instructions.
    * Incomplete or truncated responses.
    * The model defaulting to simpler tasks (like explaining instead of refactoring).
* **Code Snippet Size:** For optimal results, especially for complex tasks like Refactor or Debug, it's highly recommended to work with **smaller, focused code snippets** (e.g., single functions or classes) rather than entire files.
* **Local Performance:** Running LLMs locally requires significant computational resources (RAM and ideally a GPU). Response times will generally be slower compared to large, cloud-hosted APIs.
* **Model Capability:** While `codellama:7b-instruct` is very capable for its size, it is not as powerful as much larger models (GPT-4, Claude 3, Llama 3 70b, etc.). It may struggle with highly abstract reasoning, extremely complex code, or subtle bugs. Its instruction-following, especially for negative constraints, can sometimes be inconsistent.
* **External Factors:** Features relying on external systems (like the web scraping demo) are inherently brittle and can break if the external website changes its structure.

## Prompt Engineering & Learnings

This project involved significant iterative prompt engineering. Key takeaways include:

* **System Prompt is Key:** A detailed system prompt, clearly defining the AI's role and the expected output for *each specific task*, dramatically improved response quality and structure.
* **Structured Prompts Work:** For tasks like "Explain" and "Debug," asking for a specific, structured output format (e.g., the 3-part debug report) and reinforcing it in the system prompt yielded excellent results.
* **Instruction Following Limits (Refactor):** We discovered that `codellama:7b-instruct` strongly resists negative constraints for refactoring (i.e., "Do *not* add explanations"). Even forceful prompts failed.
* **Pivoting Goals:** Acknowledging model limitations and adjusting the goal (from "only code" to "explain + code" for refactoring) led to a successful and practical outcome. It's often better to work *with* the model's tendencies.
* **Context Window Matters:** Attempting to process large files confirmed the model's limits, reinforcing the need for chunking.
* **Simplicity Can Be Effective:** Using simple string concatenation for prompts proved more robust against copy-paste/rendering issues than multi-line f-strings in our development process.

## Demo Snippets

The project is well-suited for demonstrating its capabilities using snippets across various business domains:

* **Finance:** Black-Scholes Option Pricing.
* **Logistics:** Greedy TSP Route Finding.
* **Web Data:** Selenium-based Stock Price Scraping.
* **Data Analysis:** Pandas Sales Aggregation.

## Next Steps for Implementation

To enhance robustness and demo quality, the following improvements should be implemented in priority order:

### Phase 1: Error Handling & Resilience (Week 1 - Critical)

#### 1.1 Model Connection Error Handling
- **Current Issue:** No handling for Ollama service failures
- **Implementation:** Replace `llm = ChatOllama(model="codellama:7b-instruct")` with robust initialization that includes retry logic, connection testing, and graceful failure handling
- **Code Location:** `app_code_assistant.py:19`

#### 1.2 File Upload Validation
- **Current Issue:** No validation in `read_code_file()` function
- **Implementation:** Add file size limits (max 1MB), UTF-8 validation, and basic security checks for potentially unsafe code patterns
- **Code Location:** `app_code_assistant.py:59-60`

#### 1.3 LLM Invocation Error Handling
- **Current Issue:** No error handling around `llm.invoke()` calls
- **Implementation:** Create `safe_llm_invoke()` function with retry logic, response validation, and user-friendly error messages
- **Code Location:** `app_code_assistant.py:223-226, 248-251`

#### 1.4 Input Validation
- **Current Issue:** No validation of code input size or format
- **Implementation:** Add token estimation, size limits, and basic Python syntax validation with user warnings
- **Benefits:** Prevents context window overflow and provides better user feedback

### Phase 2: Quality Improvements (Week 2 - High Priority)

#### 2.1 Enhanced System Prompts with Examples
- **Current Issue:** Generic system prompt lacks task-specific guidance
- **Implementation:** Replace current system prompt with task-specific prompts containing structured formats and examples for Explain, Refactor, and Debug tasks
- **Code Location:** `app_code_assistant.py:156-182`
- **Expected Impact:** Dramatically improve response consistency and structure

#### 2.2 Few-Shot Prompting Implementation
- **Current Issue:** No examples provided to guide model behavior
- **Implementation:** Add `add_few_shot_examples()` function that includes high-quality input/output examples for each task type
- **Benefits:** Show the model exactly what format and quality is expected

#### 2.3 Response Quality Validation
- **Current Issue:** No validation of model output quality
- **Implementation:** Create `validate_response_quality()` function to check for completeness, proper formatting, and task-specific requirements
- **Features:** Automatic retry for poor responses, quality scoring

#### 2.4 Model Parameter Optimization
- **Current Issue:** Using default parameters not optimized for demo quality
- **Implementation:** Configure `ChatOllama` with `temperature=0.1`, `top_p=0.9`, `repeat_penalty=1.1`, and `num_ctx=4096`
- **Code Location:** `app_code_assistant.py:19`

### Phase 3: Performance Optimization (Week 3-4 - Medium Priority)

#### 3.1 Response Caching
- **Implementation:** Add `@st.cache_data` decorator with hash-based caching for identical prompts
- **Benefits:** Faster responses for repeated queries, better demo experience

#### 3.2 Code Chunking for Large Files
- **Current Issue:** Large files exceed context window and cause poor responses
- **Implementation:** Create `intelligent_code_chunking()` using AST parsing to maintain semantic boundaries
- **Features:** Automatic chunking with function/class preservation

#### 3.3 Async Processing
- **Implementation:** Add asynchronous LLM calls using `ThreadPoolExecutor` for better UI responsiveness
- **Benefits:** Non-blocking interface during model inference

#### 3.4 Memory Management
- **Implementation:** Add session state cleanup to prevent memory buildup from stored responses
- **Features:** Automatic cleanup of old responses, memory usage monitoring

### Implementation Priority Summary

1. **Week 1 (Critical):** Error handling for connection failures and file validation
2. **Week 2 (High):** Enhanced prompts with examples and response validation
3. **Week 3 (Medium):** Performance optimizations and caching
4. **Week 4 (Low):** Advanced features like chunking and async processing

### Expected Outcomes

- **Robustness:** Application handles failures gracefully without crashes
- **Demo Quality:** Consistent, well-formatted responses that showcase 7B model capabilities
- **Performance:** Faster responses and better user experience
- **Scalability:** Ability to handle larger code files and more complex tasks

### Testing Strategy

For each phase, implement comprehensive testing:
- **Error Scenarios:** Test with disconnected Ollama, corrupted files, oversized inputs
- **Quality Metrics:** Measure response consistency, format compliance, and user satisfaction
- **Performance Benchmarks:** Monitor response times, memory usage, and cache hit rates

## Future Improvements (Lower Priority)

* **Parameter Tuning:** Implement UI controls or configurations to adjust LLM parameters like `temperature`.
* **UI Enhancements:** Add options for refactoring goals or explanation detail levels.
* **Output Parsing:** Add options to extract *only* code blocks from responses if needed.
* **Model Switching:** Allow users to select different Ollama models.

## Dependencies

* streamlit
* langchain-ollama
* langchain
* numpy
* scipy
* pandas
* selenium
* webdriver-manager

---