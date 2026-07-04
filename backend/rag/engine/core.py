from typing import List, Optional
import structlog
from rag.models.schemas import (
    RegulationDocument, IncidentRecord, RAGResult, RetrievedDocument, IncidentMatch,
)
from rag.documents.kb import get_regulations, get_incidents

logger = structlog.get_logger(__name__)


class RAGEngine:
    def __init__(self):
        self.documents: List[RegulationDocument] = get_regulations()
        self.incidents: List[IncidentRecord] = get_incidents()

    def reload_kb(self) -> None:
        self.documents = get_regulations()
        self.incidents = get_incidents()
        logger.info(f"RAGEngine: loaded {len(self.documents)} docs, {len(self.incidents)} incidents")

    def retrieve(self, query: str, top_k: int = 5) -> RAGResult:
        query_lower = query.lower()
        query_tokens = query_lower.split()

        scored_docs = []
        for doc in self.documents:
            score = self._compute_relevance(doc, query_lower, query_tokens)
            if score > 0:
                scored_docs.append((doc, score))

        scored_docs.sort(key=lambda x: x[1], reverse=True)

        retrieved = []
        for doc, score in scored_docs[:top_k]:
            retrieved.append(RetrievedDocument(
                doc_id=doc.doc_id,
                source=doc.source,
                title=doc.title,
                section=doc.section,
                content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                relevance_score=round(score, 3),
                keywords=doc.keywords,
            ))

        scored_incidents = []
        for inc in self.incidents:
            score = self._compute_incident_relevance(inc, query_lower, query_tokens)
            if score > 0:
                scored_incidents.append((inc, score))

        scored_incidents.sort(key=lambda x: x[1], reverse=True)

        incident_matches = []
        for inc, score in scored_incidents[:3]:
            factors = []
            for token in query_tokens:
                if token in inc.title.lower() or token in inc.description.lower() or token in inc.root_cause.lower():
                    factors.append(token)
            incident_matches.append(IncidentMatch(
                incident=inc,
                relevance_score=round(score, 3),
                matching_factors=factors[:5],
            ))

        synthesis = self._generate_synthesis(query, retrieved, incident_matches) if retrieved else None

        return RAGResult(
            query=query,
            documents=retrieved,
            incidents=incident_matches,
            synthesis=synthesis,
        )

    def retrieve_by_signal_context(self, signal_types: List[str], zone_id: Optional[str] = None) -> RAGResult:
        query_parts = signal_types.copy()
        if zone_id:
            query_parts.append(zone_id)
        query = " ".join(query_parts)
        return self.retrieve(query, top_k=5)

    def _compute_relevance(self, doc: RegulationDocument, query_lower: str, query_tokens: List[str]) -> float:
        score = 0.0
        text = f"{doc.title} {doc.section} {doc.content} {' '.join(doc.keywords)}".lower()

        for token in query_tokens:
            if token in doc.content.lower():
                score += 3.0
            if token in doc.title.lower():
                score += 2.0
            if token in doc.section.lower():
                score += 1.0
            if token in [k.lower() for k in doc.keywords]:
                score += 4.0

        if score > 0:
            score *= 1.0 + (len([t for t in query_tokens if t in text]) / max(len(query_tokens), 1))

        return score

    def _compute_incident_relevance(self, inc: IncidentRecord, query_lower: str, query_tokens: List[str]) -> float:
        score = 0.0
        text = f"{inc.title} {inc.description} {inc.root_cause} {' '.join(inc.lessons_learned)}".lower()

        for token in query_tokens:
            if token in text:
                score += 2.0
            if token in inc.industry.lower():
                score += 1.5
            if token in inc.severity.lower():
                score += 1.0

        return score

    def _generate_synthesis(self, query: str, docs: List[RetrievedDocument], incidents: List[IncidentMatch]) -> str:
        parts = []
        if docs:
            top_doc = docs[0]
            parts.append(f"Based on {top_doc.source.value} standard '{top_doc.title}' "
                         f"(Section {top_doc.section}): {top_doc.content[:100]}...")
        if incidents:
            top_inc = incidents[0]
            parts.append(f"Related past incident: {top_inc.incident.title}. "
                         f"Root cause: {top_inc.incident.root_cause}. "
                         f"Lessons: {'; '.join(top_inc.incident.lessons_learned[:2])}.")
        if not parts:
            return "No relevant regulations or incident records found."
        return " ".join(parts)


rag_engine = RAGEngine()
