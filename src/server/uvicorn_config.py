from uvicorn.config import LOGGING_CONFIG as UVICORN_LOGGING_CONFIG

LOGGING_CONFIG = UVICORN_LOGGING_CONFIG

LOGGING_CONFIG['formatters']['access'][
    'fmt'] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
