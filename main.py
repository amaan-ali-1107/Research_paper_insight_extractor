from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import traceback
import uvicorn

from pdf_extractor import extract_text_from_pdf
from llm_service import get_insights_from_llm
from models import ArticleInsight

app = FastAPI(
    title="Life Sciences Research Article Insight Extractor",
    description="Upload a research paper PDF and get structured insights powered by AI",
    version="1.0.0"
)


@app.get("/")
def home():
    """Simple home route to check if API is running"""
    return {"message": "Life Sciences Insight Extractor API is running!"}


@app.post("/extract", response_model=ArticleInsight)
async def extract_insights(file: UploadFile = File(...)):
    """
    Main endpoint: accepts a PDF file and returns structured research insights.

    - Upload a PDF research paper
    - The API will read it, send it to the LLM, and return a structured JSON
    """

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()

    print(f"[INFO] Extracting text from: {file.filename}")
    raw_text = extract_text_from_pdf(pdf_bytes)

    if not raw_text or len(raw_text.strip()) < 100:
        raise HTTPException(status_code=422, detail="Could not extract enough text from the PDF.")

    try:
        print(f"[INFO] Sending text to LLM for analysis...")
        insights = get_insights_from_llm(raw_text, file.filename)
    except Exception as e:
        print(f"[ERROR] Something went wrong during LLM processing:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {str(e)}")

    print(f"[INFO] Done! Returning insights for: {file.filename}")
    return insights


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
