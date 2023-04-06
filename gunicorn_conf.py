from multiprocessing import cpu_count
from config.base import settings



# Socket Path

bind = f'{settings.HOST}:{settings.PORT}'

reload_engine = 'auto'

# Worker Options

workers = cpu_count() + 1

worker_class = 'uvicorn.workers.UvicornWorker'



# Logging Options

loglevel = 'error'

accesslog = f'{settings.PROJECT_HOME}/access.log'

errorlog =  f'{settings.PROJECT_HOME}/error.log'


