from rag.engine.core import rag_engine


class TestRAGEngine:
    def test_retrieve_by_keyword(self):
        result = rag_engine.retrieve("hot work gas leak", top_k=3)
        assert len(result.documents) > 0
        assert result.synthesis is not None

    def test_retrieve_incident_match(self):
        result = rag_engine.retrieve("confined space H2S fatality", top_k=5)
        assert len(result.incidents) > 0
        assert any("INC-2020-107" in i.incident.incident_id for i in result.incidents)

    def test_empty_query(self):
        result = rag_engine.retrieve("xyznonexistent12345")
        assert len(result.documents) == 0
        assert len(result.incidents) == 0

    def test_reload_kb(self):
        rag_engine.reload_kb()
        assert len(rag_engine.documents) >= 5
        assert len(rag_engine.incidents) >= 3

    def test_retrieve_by_signal_context(self):
        result = rag_engine.retrieve_by_signal_context(
            signal_types=["hot work", "gas leak"],
            zone_id="Coke Oven",
        )
        assert len(result.documents) > 0
