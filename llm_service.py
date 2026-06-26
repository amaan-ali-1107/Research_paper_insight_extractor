import os
import json
import re
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

from models import ArticleInsight
from pdf_extractor import preprocess_text

load_dotenv()


def clean_json_response(raw_response: str) -> str:
    """
    Gemini sometimes wraps its JSON in markdown code blocks like:
    ```json
    { ... }
    ```
    This function strips that away and returns clean JSON text.
    """

    raw_response = raw_response.strip()

    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_response)
    if match:
        return match.group(1).strip()

    return raw_response


def get_insights_from_llm(raw_text: str, filename: str) -> ArticleInsight:
    """
    Takes the raw extracted text from a PDF and asks the LLM to analyze it.
    Returns a structured ArticleInsight object.
    """

    clean_text = preprocess_text(raw_text)

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-3.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2,    # Low temperature = more factual, less creative
        max_output_tokens=4000
    )

    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert life sciences research analyst. 
Your job is to read research papers and extract structured information from them.
IMPORTANT: Respond with raw JSON only. No markdown, no code blocks, no explanation.
Start your response directly with {{ and end with }}.
If a field is not found in the paper, write "Not mentioned"."""
        ),
        (
            "human",
            """Analyze the following research paper and return ONLY a raw JSON object with exactly these fields:

{{
  "title": "Full title of the paper",
  "authors": ["Author 1", "Author 2"],
  "journal_or_source": "Journal name or source",
  "publication_year": "Year of publication",
  "background": "Background context and motivation of the study (2-3 sentences)",
  "hypothesis": "The main hypothesis or research question being tested",
  "methods": "Summary of the methodology used (2-3 sentences)",
  "experiment_details": "Key experimental details like sample size, conditions, tools used",
  "results": "Main results and findings (3-4 sentences)",
  "conclusions": "Conclusions drawn by the authors (2-3 sentences)",
  "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
  "limitations": "Limitations mentioned by the authors",
  "future_work": "Future directions suggested by the authors",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "plain_language_summary": "Explain this paper in simple terms that a non-scientist can understand (3-4 sentences)",
  "novelty_assessment": "What is new or unique about this research compared to existing work?",
  "related_hypotheses": [
    "A new hypothesis inspired by this paper",
    "Another follow-up hypothesis",
    "A third related research question"
  ]
}}

Research paper:

{paper_text}"""
        )
    ])

    print(f"[INFO] Calling Gemini LLM to analyze: {filename}")
    chain = prompt_template | llm
    response = chain.invoke({"paper_text": clean_text})

    raw_output = response.content
    print(f"[INFO] Got response from Gemini. Parsing JSON...")

    clean_output = clean_json_response(raw_output)

    try:
        result_dict = json.loads(clean_output)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed: {e}")
        print(f"[DEBUG] Raw output was:\n{raw_output[:500]}")
        raise ValueError(f"LLM returned invalid JSON. Error: {e}")

    return ArticleInsight(**result_dict)
