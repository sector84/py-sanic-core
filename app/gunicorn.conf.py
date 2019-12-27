from multiprocessing import cpu_count

bind = '0.0.0.0:80'
backlog = 2048
max_requests = 4096
worker_class = 'sanic.worker.GunicornWorker'
workers = cpu_count()

# accesslog = "/extern/logs/gunicorn-access.log"
# errorlog = "/extern/logs/gunicorn-error.log"

