# Sentinel Demo Storyboard

This document guides the presenter through the deterministic cinematic demonstration of Sentinel's capabilities.

## Setup
Ensure the environment is running via `make deploy`.
Open `http://localhost:3000` on a 4K display.
The platform will automatically connect via WebSocket to the live demo engine.

## Sequence 1: Mission Control Overview (0:00 - 1:30)
- **Visuals:** The 3D Interactive Plant Map rotates slowly, displaying the entire facility in isometric view.
- **Narrative:** "Welcome to Sentinel. This is not a dashboard; it's an Industrial Operating System. You are looking at the live World State of the facility."
- **Action:** Point out the Real-time Event Stream on the right panel processing thousands of frames per second. Point out the active Worker entities and machinery on the map.

## Sequence 2: The Gas Leak Hazard (1:30 - 3:00)
- **Visuals:** A red pulse emits from the Coke Oven Battery on the map. The Timeline ticks forward.
- **Narrative:** "A gas leak has just been detected by an IoT sensor. Simultaneously, the Vision Engine tracks a worker entering this precise zone to perform hot work."
- **Action:** Click on the generated event in the Timeline. The system expands the Hazard Graph, showing the linkage between `Worker -> Hot Work Permit -> High Temp Zone -> Gas Leak`.

## Sequence 3: Compound Risk Evaluation (3:00 - 4:00)
- **Visuals:** The Risk Engine panel spikes from a Safe (green) 12 to a Critical (red) 94.
- **Narrative:** "Individually, these are minor deviations. Together, they form a catastrophic compound risk. The Compliance Engine immediately flags a permit violation."

## Sequence 4: Chronos Prediction (4:00 - 5:30)
- **Visuals:** Switch to the Prediction view. The timeline shows a ghosted visualization of `t+5 minutes`.
- **Narrative:** "Instead of reacting, Sentinel predicts. Our Chronos Engine projects the trajectory of this gas cloud overlapping with the worker's path in exactly 4 minutes."

## Sequence 5: The Counterfactual Planner (5:30 - 7:00)
- **Visuals:** The Planner modal appears, overriding the screen with a glassmorphism blur. Three options are presented: `Evacuate Zone`, `Disable Machine`, `Dispatch Supervisor`.
- **Narrative:** "Sentinel doesn't just raise alarms; it solves the problem. The Counterfactual Planner has simulated three interventions and recommends an immediate targeted evacuation."
- **Action:** Click "EXECUTE". The 3D map immediately updates, showing the zone locking down. The Risk Score plunges back to green.

## Conclusion
- **Narrative:** "Sentinel didn't just record an accident. It saw the future, orchestrated a response, and prevented a catastrophe."
