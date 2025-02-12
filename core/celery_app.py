from celery import Celery

app = Celery(
    'scanner',
    broker='redis://localhost:6379/0',
    backend='db+sqlite:///scans.db'
)

app.conf.task_track_started = True
