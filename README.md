# Life Sciences Research Article Insight Extractor
 
Reading and interpreting research papers in life sciences can be time-consuming and complex, especially when trying to quickly grasp key findings, methodology, and conclusions!
 
So I present my project, the Life Sciences Research Article Insight Extractor, a GenAI-powered REST API built using FastAPI, LangChain, and Google Gemini. It accepts a research paper PDF as input and returns a structured JSON response containing comprehensive insights extracted and analyzed by an LLM.
 
## Technologies Used:
- Python (3.13)
- FastAPI (REST API)
- LangChain (LLM orchestration with prompt templates and chains)
- Google Gemini (`gemini-3.5-flash` via `langchain-google-genai`)
- PyMuPDF (PDF text extraction)
- Pydantic (structured output validation)
- python-dotenv (environment variable management)
## Project Structure:
 
```
Life_science_Insights/
├── main.py            # FastAPI app entry point — defines API routes
├── models.py          # Pydantic model defining the structured JSON output schema
├── llm_service.py     # LangChain + Gemini integration for LLM analysis
├── pdf_extractor.py   # PDF text extraction and preprocessing using PyMuPDF
├── test_api.py        # CLI script to test the API with a real PDF
├── requirements.txt   # All required Python dependencies
└── .env               # API key (hidden via .gitignore — not uploaded to GitHub)
```
 
## API Endpoints:
 
| Method | Route | Description |
|--------|------------|-------------------------------|
| GET | `/` | Health check — confirms the API is running |
| POST | `/extract` | Upload a PDF and receive structured JSON insights |
 
## Sample JSON Response:
 
```json
{
  "title": "Title of the research paper",
  "authors": ["Author One", "Author Two"],
  "journal_or_source": "Nature Biotechnology",
  "publication_year": "2024",
  "background": "Background context and motivation of the study...",
  "hypothesis": "The main hypothesis or research question being tested...",
  "methods": "Summary of the methodology used...",
  "experiment_details": "Sample size, conditions, tools, and experimental setup...",
  "results": "Main results and key findings from the study...",
  "conclusions": "Conclusions drawn by the authors...",
  "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
  "limitations": "Limitations acknowledged by the authors...",
  "future_work": "Future directions suggested by the authors...",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "plain_language_summary": "Simple explanation anyone can understand...",
  "novelty_assessment": "What is new or unique about this research...",
  "related_hypotheses": [
    "A new hypothesis inspired by this paper",
    "Another follow-up hypothesis",
    "A third related research question"
  ]
}
```
 
## How It Works:
 
The user uploads a life sciences research paper PDF to the `/extract` endpoint. PyMuPDF (`fitz`) reads the PDF bytes directly from memory — no temporary files needed — and extracts the full text page by page. The text is then preprocessed: blank lines are stripped, and papers exceeding 12,000 words are trimmed to prevent LLM token overflow while preserving key content.
 
The cleaned text is passed to a LangChain `ChatPromptTemplate` which structures a detailed system + human prompt. This chain is invoked against Google Gemini (`gemini-2.0-flash`), instructing the model to respond with raw JSON only. Since Gemini occasionally wraps output in markdown code blocks, a cleaning step strips those before parsing.
 
The parsed JSON is validated and coerced into the `ArticleInsight` Pydantic model defined in `models.py`, which enforces the expected fields and types. FastAPI automatically serializes this as the final structured JSON response.
 
## Here's a diagram describing the Data Flow:
![Data Flow](images/data_flow.png)
 
## For running on localhost:
 
- Clone the repository: `git clone https://github.com/amaan-ali-1107/Life-science-insights.git` and navigate to the project folder using `cd Life-science-insights`.
- Create a virtual environment: `python -m venv venv` and activate it using `venv\Scripts\activate` on Windows or `source venv/bin/activate` on macOS/Linux.
- Install the required dependencies: `pip install -r requirements.txt`.
- Create a `.env` file in the project root and add your Google API key:
```
  GOOGLE_API_KEY=your_google_api_key_here
```
  You can get a free API key from [Google AI Studio](https://aistudio.google.com/) — no credit card required.
 
- Run the FastAPI application: `python main.py`.
- Open your browser and go to `http://127.0.0.1:8000` to confirm the API is running, or visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.
- To test with a real PDF, run: `python test_api.py path/to/your/paper.pdf`.
## Challenges Faced and Things Learned:
 
Since this was my first Generative AI project, the biggest challenge was understanding how to bridge unstructured LLM output with a strict typed schema. LLMs like Gemini do not always return clean JSON — the model would sometimes wrap its response in markdown code blocks (` ```json ... ``` `), causing `json.loads()` to fail. I solved this by writing a `clean_json_response()` function using regex to detect and strip those code fences before parsing, which made the pipeline robust across different response formats.
 
Prompt engineering also turned out to be more nuanced than I expected. Getting Gemini to consistently return all required fields — especially the creative ones like `related_hypotheses` and `novelty_assessment` — required being very explicit in the system message and providing the exact JSON schema in the human message. I learned that instructions like "Respond with raw JSON only. Start your response directly with `{` and end with `}`" are essential to avoid non-JSON preambles that break parsing.
 
Another key learning was PDF preprocessing. Academic papers can be very long, and sending the entire extracted text to the LLM risks exceeding the model's context window. I implemented a word count check that trims the text to 12,000 words with a note appended, ensuring the API handles large papers gracefully without crashing. This also reinforced the importance of input validation — the API checks that the uploaded file is actually a PDF and that enough text was extracted before even calling the LLM.
 
Finally, structuring the project into four clearly separated files (`main.py`, `models.py`, `llm_service.py`, `pdf_extractor.py`) taught me the value of separation of concerns in API design. Each module has one job, which made debugging and iterating on the prompt much easier without touching unrelated code.