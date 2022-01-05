import logging
import logging.handlers
import os

def make_logger(LOG_DIR='outputs/logs'):
    logger = logging.getLogger(None)

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(lineno)s - %(levelname)s - %(message)s')
    
    console = logging.StreamHandler()

    PKG_DIR = os.path.dirname(os.path.realpath(__package__))
    log_dir_abs = PKG_DIR + '/' +LOG_DIR
    if not os.path.exists(log_dir_abs):
        os.makedirs(log_dir_abs)
    LOG_FILENAME = LOG_DIR + '/log'
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=LOG_FILENAME, when='midnight',interval=1, encoding='utf-8', utc=True)
    file_handler.suffix = '%y%m%d.log'

    console.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger