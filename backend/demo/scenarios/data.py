from demo.models.schemas import Scenario, ScenarioStage, DemoAction, DemoActionType

SCENARIOS = [
    Scenario(
        scenario_id="DEMO_01",
        name="Gas Leak + Hot Work Permit",
        description="Sentinel predicts an explosion due to rising gas and active hot work, recommending an intervention.",
        stages=[
            ScenarioStage(
                stage_num=1,
                name="Normal Operation",
                narration="Operations in the Coke Oven Battery are proceeding normally. Background gas sensors are stable.",
                actions=[
                    DemoAction(type=DemoActionType.UPDATE_STATE, payload={"zone": "Coke Oven", "gas_level": 5})
                ]
            ),
            ScenarioStage(
                stage_num=2,
                name="Permit Issued",
                narration="A Hot Work Permit is issued for maintenance in the Coke Oven.",
                actions=[
                    DemoAction(type=DemoActionType.UPDATE_STATE, payload={"zone": "Coke Oven", "permit_active": True})
                ]
            ),
            ScenarioStage(
                stage_num=3,
                name="Gas Increases",
                narration="Gas concentration has increased by 28% over the last 12 minutes.",
                actions=[
                    DemoAction(type=DemoActionType.UPDATE_STATE, payload={"zone": "Coke Oven", "gas_level": 45})
                ]
            ),
            ScenarioStage(
                stage_num=4,
                name="Prediction & Intervention",
                narration="Chronos predicts explosion probability will reach 91%. Counterfactual Planner recommends delaying Hot Work.",
                actions=[
                    DemoAction(type=DemoActionType.UPDATE_STATE, payload={"zone": "Coke Oven", "gas_level": 85}),
                    DemoAction(type=DemoActionType.TRIGGER_PLAN, payload={"plan": "Suspend Hot Work"})
                ]
            )
        ]
    ),
    Scenario(
        scenario_id="DEMO_02",
        name="Confined Space Entry + Toxic Gas",
        description="Sentinel detects a worker entering a confined space with rising H2S levels.",
        stages=[
            ScenarioStage(
                stage_num=1,
                name="Worker Enters",
                narration="Worker John Doe enters the confined storage tank for inspection.",
                actions=[]
            ),
            ScenarioStage(
                stage_num=2,
                name="Toxic Gas Detected",
                narration="H2S levels rise rapidly in the tank.",
                actions=[]
            )
        ]
    ),
    Scenario(
        scenario_id="DEMO_03",
        name="Forklift + Blind Corner + Worker",
        description="Sentinel Vision Engine detects an unsafe trajectory.",
        stages=[
            ScenarioStage(
                stage_num=1,
                name="Forklift Approaches",
                narration="Forklift 02 is approaching the blind corner in Warehouse B.",
                actions=[]
            ),
            ScenarioStage(
                stage_num=2,
                name="Worker Detected",
                narration="Vision detects a worker walking into the forklift's path. Alert dispatched.",
                actions=[
                    DemoAction(type=DemoActionType.EMIT_VISION, payload={"event": "FORKLIFT_NEAR_WORKER"})
                ]
            )
        ]
    )
]

def get_scenario(scenario_id: str) -> Scenario:
    return next((s for s in SCENARIOS if s.scenario_id == scenario_id), None)
