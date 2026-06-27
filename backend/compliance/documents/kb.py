from compliance.models.schemas import RegulationReference, RegulationBody

class RegulationKnowledgeBase:
    """
    Mocked database of regulatory standards.
    """
    
    @staticmethod
    def get_oisd_117_hot_work() -> RegulationReference:
        return RegulationReference(
            document_id="OISD-STD-117",
            body=RegulationBody.OISD,
            title="Fire Protection Facilities for Petroleum Depots",
            section="4.2 Hot Work Permits",
            clause_text="Hot work shall not be permitted in any zone where combustible gas concentration exceeds 20% of the Lower Explosive Limit (LEL)."
        )

    @staticmethod
    def get_factories_act_confined_space() -> RegulationReference:
        return RegulationReference(
            document_id="FACTORIES-ACT-1948",
            body=RegulationBody.FACTORIES_ACT,
            title="The Factories Act, 1948",
            section="Section 36: Precautions against dangerous fumes",
            clause_text="No person shall be required or allowed to enter any confined space until all practicable measures have been taken to remove any gas, fume, or dust."
        )

    @staticmethod
    def get_internal_ppe_policy() -> RegulationReference:
        return RegulationReference(
            document_id="SOP-PPE-001",
            body=RegulationBody.INTERNAL_SOP,
            title="Standard Operating Procedure for Personal Protective Equipment",
            section="2.1 Zone Specific PPE",
            clause_text="Workers in HIGH or CRITICAL hazard zones must wear full PPE including Hard Hat, Safety Goggles, and Fire Retardant Clothing."
        )

knowledge_base = RegulationKnowledgeBase()
