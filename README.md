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

## Prompt Engineering & Learnings

This project involved significant iterative prompt engineering. Key takeaways include:

* **System Prompt is Key:** A detailed system prompt, clearly defining the AI's role and the expected output for *each specific task*, dramatically improved response quality and structure.
* **Structured Prompts Work:** For tasks like "Explain" and "Debug," asking for a specific, structured output format (e.g., the 3-part debug report) and reinforcing it in the system prompt yielded excellent results.
* **Instruction Following Limits (Refactor):** We discovered that `codellama:7b-instruct` strongly resists negative constraints for refactoring (i.e., "Do *not* add explanations"). Even forceful prompts failed.
* **Pivoting Goals:** Acknowledging model limitations and adjusting the goal (from "only code" to "explain + code" for refactoring) led to a successful and practical outcome. It's often better to work *with* the model's tendencies than to fight them, especially when the alternative output is still valuable.
* **Context Window Matters:** Attempting to process large files (like the entire application script) confirmed that the 7b model hits context limits, leading to incomplete or irrelevant responses. **Chunking** (processing smaller pieces) is essential for large inputs.
* **Simplicity Can Be Effective:** Our final `build_prompt` function uses simple string concatenation, which proved more robust against potential rendering/copy-paste issues than complex multi-line f-strings in the development environment.

## Demo Snippets

The project includes several demo snippets (or can be used with them) to showcase its capabilities across various business domains:

* **Finance:** Black-Scholes Option Pricing.
* **Logistics:** Greedy TSP Route Finding.
* **Web Data:** Selenium-based Stock Price Scraping.
* **Data Analysis:** Pandas Sales Aggregation.

These allow for demonstrating explanation, refactoring (e.g., `iterrows` to `groupby`), and debugging (e.g., broken web selectors, division by zero).

## Future Improvements

* **Parameter Tuning:** Implement UI controls or configurations to adjust LLM parameters like `temperature`.
* **Few-Shot Prompting:** Add few-shot examples to prompts for tasks requiring highly specific output formats.
* **UI Enhancements:** Add options for refactoring goals or explanation detail levels.
* **Automated Input Chunking:** Automatically handle large code files by breaking them down.
* **Output Parsing:** Add options to extract *only* code blocks from responses if needed.
* **Error Handling:** Improve robustness within the Streamlit app.
* **Model Switching:** Allow users to select different Ollama models.

---