import logging.handlers
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
#import logging_loki
from multiprocessing import Queue
import sys
import os

def set_loggers():

    """
    Formatters intentionally use :: as a delimeter, no white space
    That way messages can be used with awk -F='::' and not worry about white space in messages

    """
    if not os.path.exists('/logs-volume/app'):
        os.makedirs('/logs-volume/app')

    if not os.path.exists('/logs-volume/fixlogs'):
        os.makedirs('/logs-volume/fixlogs')


    # setup profiler logger
    profiler_queue = Queue(-1)
    p_queue_handler = QueueHandler(profiler_queue)

    logger = logging.getLogger("profiler")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(p_queue_handler)

    file_handler = TimedRotatingFileHandler('/logs-volume/app/function-times.log', backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    std_handler.setFormatter(formatter)

    p_listener = QueueListener(profiler_queue, file_handler, std_handler, respect_handler_level=True)
    p_listener.start()

    #  Loki logger
    #handler = logging_loki.LokiQueueHandler(
    #             Queue(-1),
    #             url="http://loki:3100/loki/api/v1/push",
    #             tags={"application": "fastapi-orderbook"},
    #             auth=("admin", "admin"),
    #             version="1"
    #)

    # fix log handler
    
    fix_queue = Queue(-1)
    fix_queue_handler = QueueHandler(fix_queue)

    fix_logger = logging.getLogger("fix")
    fix_logger.setLevel(logging.DEBUG)
    fix_logger.addHandler(fix_queue_handler)

    fix_file_handler = TimedRotatingFileHandler('/logs-volume/fixlogs/fixlogs.log', when="M", backupCount=10)
    fix_file_handler.setLevel(logging.DEBUG)

    
    fix_formatter = logging.Formatter('%(message)s')
    fix_file_handler.setFormatter(fix_formatter)
    
    fix_stdh = logging.StreamHandler(sys.stdout)
    fix_stdh.setLevel(logging.DEBUG)
    fix_stdh.setFormatter(fix_formatter)
    
    fix_listener = QueueListener(fix_queue, fix_stdh, fix_file_handler,respect_handler_level=True)
    fix_listener.start()

    # general logger
    queue = Queue(-1)
    queue_handler = QueueHandler(queue)

    glogger = logging.getLogger('general')
    glogger.setLevel(logging.DEBUG)
    glogger.addHandler(queue_handler)

    logFormatter = logging.Formatter(fmt='%(message)s::%(asctime)s')

    stdh = logging.StreamHandler(sys.stdout)
    stdh.setLevel(logging.INFO)
    stdh.setFormatter(logFormatter)

    info_handler = TimedRotatingFileHandler('/logs-volume/app/info.log', backupCount=10)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logFormatter)

    debug_handler = TimedRotatingFileHandler('/logs-volume/app/debug.log', backupCount=10)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logFormatter)

    error_handler = TimedRotatingFileHandler('/logs-volume/app/error.log', backupCount=10)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logFormatter)

    warning_handler = TimedRotatingFileHandler('/logs-volume/app/warning.log', backupCount=10)
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(logFormatter)

    listener = QueueListener(queue, stdh, warning_handler, info_handler, debug_handler, error_handler,respect_handler_level=True)
    listener.start()

    # http log handler
    
    http_queue = Queue(-1)
    http_queue_handler = QueueHandler(http_queue)

    http_logger = logging.getLogger("http")
    http_logger.setLevel(logging.DEBUG)
    http_logger.addHandler(http_queue_handler)

    http_file_handler = TimedRotatingFileHandler('/logs-volume/app/http.log', when="M", backupCount=10)
    http_file_handler.setLevel(logging.DEBUG)

    
    http_formatter = logging.Formatter('%(message)s')
    http_file_handler.setFormatter(http_formatter)
    
    http_stdh = logging.StreamHandler(sys.stdout)
    http_stdh.setLevel(logging.DEBUG)
    http_stdh.setFormatter(http_formatter)
    
    http_listener = QueueListener(http_queue, http_stdh, http_file_handler,respect_handler_level=True)
    http_listener.start()


