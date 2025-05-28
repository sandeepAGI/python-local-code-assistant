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

## Future Improvements

* **Parameter Tuning:** Implement UI controls or configurations to adjust LLM parameters like `temperature`.
* **Few-Shot Prompting:** Add few-shot examples to prompts for tasks requiring highly specific output formats.
* **UI Enhancements:** Add options for refactoring goals or explanation detail levels.
* **Automated Input Chunking:** Automatically handle large code files by breaking them down.
* **Output Parsing:** Add options to extract *only* code blocks from responses if needed.
* **Error Handling & Retries:** Enhance the Streamlit app to handle LLM errors more gracefully.
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