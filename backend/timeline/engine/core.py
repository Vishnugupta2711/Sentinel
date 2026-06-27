from timeline.storage.store import TimelineStore
from timeline.compression.manager import CompressionManager
from timeline.queries.engine import QueryEngine
from timeline.analytics.engine import TimelineAnalytics
from timeline.replay.manager import ReplayManager

class TimelineEngine:
    """Composition root for the Sentinel Historical Timeline Engine."""
    
    def __init__(self):
        self.store = TimelineStore(max_capacity=1000)
        
        # Modules
        self.compression = CompressionManager(self.store, keep_uncompressed=100)
        self.queries = QueryEngine(self.store)
        self.analytics = TimelineAnalytics(self.queries)
        self.replay = ReplayManager(self.store)

    def startup(self):
        self.compression.start()

    def shutdown(self):
        self.compression.stop()
        self.replay.pause()

# Singleton for FastAPI routes
timeline_engine = TimelineEngine()

def get_timeline_engine() -> TimelineEngine:
    return timeline_engine
