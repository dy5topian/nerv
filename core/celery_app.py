from celery import Celery
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery(
    'scanner',
    broker='redis://localhost:6379/0',
    backend='db+sqlite:///scans.db',
    include=[
        'agents.nmap_agent',
        'agents.whatweb_agent',
        'utils.orchestrator',  # Make sure this is included
        'core.celery_app'
    ]
)

# Configure Celery
app.conf.task_track_started = True

# Import tasks

# Optional: Add a simple task to test the setup
@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')
