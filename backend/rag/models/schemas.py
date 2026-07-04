from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now


class RegulationSource(str, Enum):
    OISD = "OISD"
    FACTORIES_ACT = "FACTORIES_ACT"
    DGMS = "DGMS"
    INTERNAL_SOP = "INTERNAL_SOP"


class IncidentRecord(BaseModel):
    incident_id: str
    title: str
    description: str
    industry: str
    root_cause: str
    severity: str
    regulation_refs: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)


class RegulationDocument(BaseModel):
    doc_id: str
    source: RegulationSource
    title: str
    section: str
    content: str
    keywords: List[str] = Field(default_factory=list)


class RetrievalQuery(BaseModel):
    query: str
    top_k: int = 5
    filters: Dict[str, Any] = Field(default_factory=dict)


class RetrievedDocument(BaseModel):
    doc_id: str
    source: RegulationSource
    title: str
    section: str
    content: str
    relevance_score: float
    keywords: List[str] = Field(default_factory=list)


class IncidentMatch(BaseModel):
    incident: IncidentRecord
    relevance_score: float
    matching_factors: List[str] = Field(default_factory=list)


class RAGResult(BaseModel):
    query: str
    documents: List[RetrievedDocument] = Field(default_factory=list)
    incidents: List[IncidentMatch] = Field(default_factory=list)
    synthesis: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
