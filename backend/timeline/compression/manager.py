import asyncio
import structlog
from timeline.storage.store import TimelineStore

logger = structlog.get_logger(__name__)

class CompressionManager:
    """Background manager to compress older timeline entries to save memory."""
    
    def __init__(self, store: TimelineStore, keep_uncompressed: int = 100):
        self.store = store
        self.keep_uncompressed = keep_uncompressed
        self._running = False
        self._task = None

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
            logger.info("Timeline Compression Manager started.")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def _loop(self):
        while self._running:
            try:
                # Find older entries that haven't been compressed
                targets = self.store.get_uncompressed_entries(keep_last=self.keep_uncompressed)
                if targets:
                    logger.debug(f"Compressing {len(targets)} old timeline entries...")
                    for entry in targets:
                        entry.compress()
            except Exception as e:
                logger.error(f"Error in compression manager: {e}")
                
            # Run this check every 10 seconds
            await asyncio.sleep(10.0)
