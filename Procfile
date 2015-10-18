web: gunicorn -c gunicorn.cfg wuphf.app:app
worker: celery worker -A wuphf.app.celery 
