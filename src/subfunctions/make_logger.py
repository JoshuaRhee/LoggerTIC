import datetime
import logging
import logging.handlers
import time
import os

class DailyRotatingFileHandler(logging.handlers.RotatingFileHandler):

    def __init__(self, basedir, alias='', mode='a', maxBytes=10000, backupCount=10, encoding=None, delay=0):
        
        # @summary: 
        # Set self.baseFilename to date string of today.
        # The handler create logFile named self.baseFilename

        self.basedir_ = basedir
        #self.alias_ = alias
        self.last_backup_cnt = 0

        self.baseFilename = self.getBaseFilename()

        logging.handlers.RotatingFileHandler.__init__(self, self.baseFilename, mode, maxBytes, backupCount, encoding, delay)

    def getBaseFilename(self):
        # @summary: Return logFile name string formatted to "today.log.alias"
        self.today_ = datetime.date.today()
        basename_ = "log." + self.today_.strftime("%y%m%d")# + self.alias_
        return os.path.join(self.basedir_, basename_)

    def shouldRollover(self, record):
        # @summary: 
        # Rollover happen 
        # 1. When the logFile size is get over maxBytes.
        # 2. When date is changed.
        # @see: BaseRotatingHandler.emit

        if self.stream is None:                
            self.stream = self._open()

        if self.maxBytes > 0 :                  
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1

        if self.today_ != datetime.date.today():
            self.baseFilename = self.getBaseFilename()
            return 1

        return 0
    
    # override
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # my code starts here
        self.last_backup_cnt += 1
        nextName = "%s.%d" % (self.baseFilename, self.last_backup_cnt)
        self.rotate(self.baseFilename, nextName)
        # my code ends here
        if not self.delay:
            self.stream = self._open()
            

def make_logger(LOG_DIR='outputs/logs'):
    logger = logging.getLogger(None)

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(lineno)s - %(levelname)s - %(message)s')
    
    console = logging.StreamHandler()

    PKG_DIR = os.path.dirname(os.path.realpath(__package__))
    log_dir_abs = PKG_DIR + '/' +LOG_DIR
    if not os.path.exists(log_dir_abs):
        os.makedirs(log_dir_abs)
    #LOG_FILENAME = LOG_DIR + '/log'
    #file_handler = logging.handlers.TimedRotatingFileHandler(filename=LOG_FILENAME, when='midnight',interval=1, encoding='utf-8', utc=True)
    fileMaxByte = 1024 * 1024 * 200 # [MB]
    file_handler = DailyRotatingFileHandler(LOG_DIR, maxBytes=fileMaxByte)
    file_handler.suffix = '%y%m%d.log.txt'

    console.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logging.Formatter.converter = time.gmtime

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger