from fastapi import APIRouter

from api.routers import health

from intelligence.routes.api import router as intelligence_router
from intelligence.websocket.live import router as intelligence_ws_router
from hazard_graph.routes.api import router as graph_router
from hazard_graph.websocket.live import router as graph_ws_router
from chronos.api.routes import router as chronos_router
from chronos.websocket.live import router as chronos_ws_router
from risk.api.routes import router as risk_router
from risk.websocket.live import router as risk_ws_router
from planner.api.routes import router as planner_router
from planner.websocket.live import router as planner_ws_router
from compliance.api.routes import router as compliance_router
from compliance.websocket.live import router as compliance_ws_router
from vision.api.routes import router as vision_router
from vision.websocket.live import router as vision_ws_router
from demo.api.routes import router as demo_router
from demo.websocket.live import router as demo_ws_router
from debrief.api.router import router as debrief_router
from debrief.api.websocket import router as debrief_ws_router
from investigation.api.router import router as investigation_router
from investigation.api.websocket import router as investigation_ws_router

# Phase 7: Multi-agent compound risk routes
from correlation.api.routes import router as correlation_router
from correlation.websocket.live import router as correlation_ws_router
from rag.api.routes import router as rag_router
from rag.websocket.live import router as rag_ws_router
from alerts.api.routes import router as alerts_router
from alerts.websocket.live import router as alerts_ws_router

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(intelligence_router)
api_router.include_router(intelligence_ws_router)
api_router.include_router(graph_router)
api_router.include_router(graph_ws_router)
api_router.include_router(chronos_router)
api_router.include_router(chronos_ws_router)
api_router.include_router(risk_router)
api_router.include_router(risk_ws_router)
api_router.include_router(planner_router)
api_router.include_router(planner_ws_router)
api_router.include_router(compliance_router)
api_router.include_router(compliance_ws_router)
api_router.include_router(vision_router)
api_router.include_router(vision_ws_router)
api_router.include_router(demo_router)
api_router.include_router(demo_ws_router)
api_router.include_router(debrief_router, prefix="/debrief")
api_router.include_router(debrief_ws_router)
api_router.include_router(investigation_router, prefix="/investigation")
api_router.include_router(investigation_ws_router)

# Phase 7: Multi-agent compound risk routes
api_router.include_router(correlation_router)
api_router.include_router(correlation_ws_router)
api_router.include_router(rag_router)
api_router.include_router(rag_ws_router)
api_router.include_router(alerts_router)
api_router.include_router(alerts_ws_router)
