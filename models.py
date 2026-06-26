from pydantic import BaseModel
from typing import List, Optional


class ArticleInsight(BaseModel):
    """
    This is the structured output that our API returns for every research paper.
    Every field here will appear in the final JSON response.
    """

    title: str
    authors: List[str]
    journal_or_source: Optional[str] = "Not mentioned"
    publication_year: Optional[str] = "Not mentioned"

    background: str
    hypothesis: str
    methods: str
    experiment_details: str
    results: str
    conclusions: str

    key_findings: List[str]
    limitations: Optional[str] = "Not mentioned"
    future_work: Optional[str] = "Not mentioned"
    keywords: List[str]

    plain_language_summary: str        # Simple explanation anyone can understand
    novelty_assessment: str            
    related_hypotheses: List[str]      # New hypotheses inspired by this paper
