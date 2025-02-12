from celery import Celery
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery(
    'scanner',
    broker='redis://localhost:6379/0',
    backend='db+sqlite:///scans.db'
)

# Ensure tasks are discovered
app.autodiscover_tasks(['agents.nmap_agent', 'agents.whatweb_agent'])

app.conf.task_track_started = True

# Optional: Add a simple task to test the setup
@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')
