from typing import List
from rag.models.schemas import RegulationDocument, IncidentRecord, RegulationSource

OISD_DOCUMENTS = [
    RegulationDocument(
        doc_id="OISD-117-1",
        source=RegulationSource.OISD,
        title="OISD Standard 117: Fire Protection Facilities for Petroleum Depots",
        section="3.2 Hot Work",
        content="Hot work permits shall be valid only for the specific location and duration of the work. "
                "A gas test must be conducted within 30 minutes prior to commencing hot work. "
                "If hydrocarbons are detected at 10% or more of the Lower Explosive Limit (LEL), "
                "hot work shall be immediately suspended until the area is declared safe.",
        keywords=["hot work", "gas test", "LEL", "permit", "hydrocarbons", "fire protection"],
    ),
    RegulationDocument(
        doc_id="OISD-117-2",
        source=RegulationSource.OISD,
        title="OISD Standard 117: Fire Protection Facilities for Petroleum Depots",
        section="4.1 Gas Detection",
        content="Continuous gas monitoring shall be installed in all areas handling hydrocarbons. "
                "Alarm set points shall be at 20% LEL for warning and 40% LEL for high alarm. "
                "All gas detection systems shall be calibrated every 30 days.",
        keywords=["gas monitoring", "LEL", "alarm", "calibration", "hydrocarbons"],
    ),
    RegulationDocument(
        doc_id="OISD-118-1",
        source=RegulationSource.OISD,
        title="OISD Standard 118: Static Electricity",
        section="5.0 Confined Space",
        content="Entry into confined spaces where flammable atmospheres may exist requires: "
                "(a) continuous gas monitoring, (b) forced ventilation, "
                "(c) full body harness with retrieval line, (d) standby man at the entrance. "
                "Atmospheres exceeding 25% LEL require immediate evacuation.",
        keywords=["confined space", "gas monitoring", "ventilation", "evacuation", "LEL"],
    ),
    RegulationDocument(
        doc_id="OISD-GDN-1",
        source=RegulationSource.OISD,
        title="OISD Guidelines: Permit to Work System",
        section="2.0 Permit Types",
        content="The permit to work system shall cover: (a) Hot Work permits, "
                "(b) Confined Space Entry permits, (c) Excavation permits, "
                "(d) Electrical Work permits, (e) Height Work permits. "
                "Each permit type shall have specific risk assessment and control measure requirements.",
        keywords=["permit", "hot work", "confined space", "risk assessment", "PTW"],
    ),
    RegulationDocument(
        doc_id="OISD-144-1",
        source=RegulationSource.OISD,
        title="OISD Standard 144: Safety Management System",
        section="7.0 Shift Handover",
        content="A formal shift handover procedure shall be implemented at all operating facilities. "
                "The handover shall include: (a) current plant status, (b) ongoing permits, "
                "(c) equipment out of service, (d) abnormal conditions, "
                "(e) instructions for the incoming shift. Written records shall be maintained.",
        keywords=["shift handover", "permit", "plant status", "safety management"],
    ),
]

FACTORIES_ACT_DOCUMENTS = [
    RegulationDocument(
        doc_id="FA-1923-1",
        source=RegulationSource.FACTORIES_ACT,
        title="Factories Act, 1923: Chapter IV — Safety",
        section="Section 21A: Confined Space",
        content="No person shall be required or allowed to enter any confined space "
                "until all practical steps have been taken to remove any fumes or to prevent "
                "ingress of fumes and a certificate in writing has been given by a competent person "
                "that the space is safe for entry without breathing apparatus.",
        keywords=["confined space", "fumes", "certificate", "safe entry", "breathing apparatus"],
    ),
    RegulationDocument(
        doc_id="FA-1923-2",
        source=RegulationSource.FACTORIES_ACT,
        title="Factories Act, 1923: Chapter IV — Safety",
        section="Section 21B: Gas Testing",
        content="Where any person is to enter a confined space, the atmosphere shall be tested "
                "for the presence of flammable or toxic gases. Testing shall be carried out "
                "by a competent person using appropriate gas detection equipment.",
        keywords=["gas testing", "confined space", "atmosphere", "flammable", "toxic"],
    ),
]

INTERNAL_SOP_DOCUMENTS = [
    RegulationDocument(
        doc_id="SOP-PPE-1",
        source=RegulationSource.INTERNAL_SOP,
        title="SOP: Personal Protective Equipment",
        section="3.0 High Hazard Zones",
        content="All personnel entering high hazard zones shall wear: (a) hard hat, "
                "(b) safety glasses, (c) steel-toed boots, (d) flame-resistant clothing, "
                "(e) appropriate respiratory protection based on zone classification.",
        keywords=["PPE", "hard hat", "safety glasses", "respiratory", "high hazard"],
    ),
    RegulationDocument(
        doc_id="SOP-EMERG-1",
        source=RegulationSource.INTERNAL_SOP,
        title="SOP: Emergency Response",
        section="2.0 Evacuation",
        content="Upon detection of a critical gas leak or fire hazard, the zone shall be "
                "evacuated immediately. The safety officer shall account for all personnel "
                "at the designated assembly point. No re-entry shall be permitted "
                "until the zone is declared safe by authorized personnel.",
        keywords=["evacuation", "gas leak", "fire", "assembly point", "safe re-entry"],
    ),
]

INCIDENT_CORPUS = [
    IncidentRecord(
        incident_id="INC-2019-042",
        title="Gas Explosion During Hot Work — Petroleum Storage Facility",
        description="During hot work on a pipeline near a storage tank, "
                    "accumulated hydrocarbon vapors ignited, causing a catastrophic explosion. "
                    "The hot work permit had been issued 4 hours prior without re-testing for gas.",
        industry="Petroleum",
        root_cause="Failure to re-test atmosphere for flammable gases before commencing hot work. "
                   "Gas detection system had been bypassed for maintenance.",
        severity="CRITICAL",
        regulation_refs=["OISD-117-1", "OISD-117-2"],
        lessons_learned=[
            "Atmosphere must be tested immediately before hot work commences",
            "Gas detection systems should never be bypassed during maintenance operations",
            "Permit validity should be limited to 2 hours without re-testing",
        ],
    ),
    IncidentRecord(
        incident_id="INC-2020-107",
        title="Confined Space Fatality — H2S Exposure",
        description="A worker entered a storage tank without continuous gas monitoring. "
                    "H2S levels had risen to 500 ppm due to bacterial breakdown of organic material. "
                    "The confined space entry permit did not specify gas testing requirements.",
        industry="Chemical",
        root_cause="Inadequate permit conditions: no gas testing requirement specified. "
                   "Confined space entry procedure not followed.",
        severity="CRITICAL",
        regulation_refs=["OISD-118-1", "FA-1923-1", "FA-1923-2"],
        lessons_learned=[
            "Continuous gas monitoring is mandatory for confined space entry",
            "Permits must specify all safety requirements explicitly",
            "Standby personnel must be trained in rescue procedures",
        ],
    ),
    IncidentRecord(
        incident_id="INC-2021-033",
        title="Shift Handover Failure Leads to Chemical Spill",
        description="During shift changeover, the outgoing shift failed to communicate "
                    "that a reactor pressure was rising abnormally. The incoming shift was unaware "
                    "until the relief valve lifted, releasing toxic chemicals.",
        industry="Chemical",
        root_cause="Inadequate shift handover procedure. No written handover record maintained. "
                   "Abnormal conditions not communicated.",
        severity="HIGH",
        regulation_refs=["OISD-144-1"],
        lessons_learned=[
            "Written shift handover records are essential for critical plant parameters",
            "Abnormal conditions must be explicitly highlighted during handover",
            "Both shifts should conduct a joint walk-through when possible",
        ],
    ),
    IncidentRecord(
        incident_id="INC-2022-089",
        title="Near Miss: Forklift-Worker Collision at Blind Corner",
        description="A forklift operator turned a blind corner at speed and narrowly missed "
                    "a worker walking in the same aisle. The warehouse had no segregation "
                    "between pedestrian and vehicle traffic.",
        industry="Manufacturing",
        root_cause="Lack of pedestrian-vehicle segregation. No warning system at blind corners. "
                   "Forklift speed not governed.",
        severity="MEDIUM",
        regulation_refs=[],
        lessons_learned=[
            "Pedestrian walkways should be physically separated from vehicle routes",
            "Blind corners should have mirrors or sensor-based warning systems",
            "Forklift speed limiters should be installed in indoor areas",
        ],
    ),
]


def get_regulations() -> List[RegulationDocument]:
    return OISD_DOCUMENTS + FACTORIES_ACT_DOCUMENTS + INTERNAL_SOP_DOCUMENTS


def get_incidents() -> List[IncidentRecord]:
    return INCIDENT_CORPUS
