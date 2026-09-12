# The Rulebook That Argues With Itself

A highly rigorous Retrieval-Augmented Generation (RAG) system built to parse complex, contradictory institutional rulebooks.

Unlike standard LLM chatbots that "hallucinate" confidence or smooth over conflicting information, this system acts as a strict compliance auditor. It evaluates user queries against a university handbook and lands in one of three verifiable states:

1. **CONSENSUS**: The rulebook provides a clear, undisputed answer.
2. **UNANSWERABLE**: The rulebook does not contain the answer (the system explicitly refuses to guess or use negative inference).
3. **CONTRADICTION**: The rulebook contains conflicting clauses (e.g., Clause A strictly forbids X, while Clause B permits it).

## Tech Stack

- **LLM Reasoning**: Google Gemini (via `google-genai` SDK)
- **Vector Retrieval**: ChromaDB (Persistent local storage)
- **UI**: Streamlit
- **Environment**: `python-dotenv`

## Project Structure

- `core_engine.py`: The modular business logic. Handles smart MD5-hashed document ingestion, ChromaDB querying, and the strict zero-shot JSON prompting pipeline.
- `app.py`: The Streamlit chat interface featuring exact-quote extraction and traceable chunk expansion.
- `evaluate.py`: An automated testing script that runs 25 adversarial queries to generate a Confusion Matrix and accuracy report.
- `data/rulebook.md`: The corpus containing planted contradictions.
- `eval_set.json`: The adversarial test queries.

## Setup and Installation

**1. Clone the repository**

```bash
git clone https://github.com/chetankhairnar05/Rulebook_argue_itself_project.git
cd Rulebook_argue_itself_project
```

**2. Create and activate a virtual environment**

```bash
# On Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up your API Key**

Create a file named `.env` in the root directory and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

## Usage

**To run the user interface:**

```bash
streamlit run app.py
```

> **Note:** The system features smart file-hashing. It will automatically get detected if `data/rulebook.md` has been modified and will seamlessly rebuild the vector database if needed.

**To run the automated evaluation script:**

```bash
python evaluate.py
```

This script bypasses the UI and stress-tests the AI against the 25 adversarial test cases in `eval_set.json`, printing a confusion matrix to the terminal and generating an `eval_report.md` file.
