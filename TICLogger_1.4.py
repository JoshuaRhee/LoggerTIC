#######################################
# Time Interval Counter Logger
# Device: 53230A, 53131A, 53132A, SR620
# Version: 1.4
# * Debugging in logging limitation problem
#######################################

import os
import configparser
import pyvisa
from datetime import datetime, timedelta
from date2mjd import date2mjd
import logging
import logging.handlers
from pytictoc import TicToc

class Instrument:
    ## CONSTRUCTOR
    def __init__(self, config_section, numInst):
        self.missed = 0
        # try:
        self.flag_init = False
        self.config_section = config_section
        if config_section.has_section('INST'+str(numInst)):
            self.config = config_section['INST'+str(numInst)]
            self.inst = self.connectInst(numInst)
            if self.inst:
                if self.applyOptions(numInst):
                    self.flag_init = True
                else:
                    pass
            else:
                logger.error(f'@__init__: Both GPIB and TCPIP connection were failed for [INST{str(numInst)}].')
        else:
            pass
        # except:
        #     logger.critical('@__init__: Unexpected error occurred for [INST' + str(numInst) + '].')

    ## CONNECT TO THE INSTRUMENT
    def connectInst(self, numInst):
        if not self.config_section.has_option('INST'+str(numInst), 'INTERFACE'):
            logger.error('@connectInst: There is no INTERFACE option in section [INST' + str(numInst) + '].')
            return None
        else:
            if self.config['INTERFACE'] == 'TCPIP_INSTR':
                try:
                    IPaddr = self.config['ADDRESS']
                    rm = pyvisa.ResourceManager()
                    rm.list_resources()
                    (f'TCPIP0::{IPaddr}::inst0::INSTR')
                    Instrument = rm.open_resource(f'TCPIP0::{IPaddr}::inst0::INSTR')
                    self.instModel = Instrument.query('*IDN?').split(',')[1]
                    logger.info(f'@connectInst: Connect to TCPIP ({IPaddr}).')
                    return Instrument
                except:
                    logger.error(f'@connectInst: Failed to connect to TCP/IP ({IPaddr}).')
                    return None
            elif self.config['INTERFACE'] == 'TCPIP_SOCKET':
                return None
            elif self.config['INTERFACE'] == 'GPIB_INSTR':
                try:
                    GPIBaddr = self.config['ADDRESS']
                    rm = pyvisa.ResourceManager()
                    rm.list_resources()
                    (f'GPIB0::{GPIBaddr}::INSTR')
                    Instrument = rm.open_resource(f'GPIB0::{GPIBaddr}::INSTR')
                    self.instModel = Instrument.query('*IDN?').split(',')[1]
                    logger.info(f'@connectInst: Connected to GPIB ({GPIBaddr}).')
                    return Instrument
                except:
                    logger.error(f'@connectInst: Failed to connect to GPIB ({GPIBaddr}).')
                    return None
            elif self.config['INTERFACE'] == 'SERIAL_INSTR':
                return None
            elif self.config['INTERFACE'] == 'ENET-SERIAL_INSTR':
                return None
            else:
                logger.error('@connectInst: INTERFACE option is not appropriate.')
                return None

    ## APPLY PRESET OPTIONS
    def applyOptions(self, numInst):
        try:
            # Check FILE_ID option
            if self.config_section.has_option('INST'+str(numInst), 'FILE_ID'):
                self.instID = self.config['FILE_ID']
            else:
                logger.error(f'@__init__: There is no FILE_ID option in a section [INST{str(numInst)}].')
                return False

            # Check TIMESTAMP option
            if self.config_section.has_option('INST'+str(numInst), 'TIMESTAMP'):
                self.timestamp = self.config['TIMESTAMP']
                if self.timestamp not in ['SUP','DUP','SER']:
                    self.timestamp='SUP'
                    logger.warning('@initInst: Improper TIMETAG option in .ini file. Set SUP as a default.')
            else:
                self.timestamp='SUP'
                logger.warning('@initInst: No TIMESTAMP option in .ini file. Set SUP as a default.')

            # Check other options
            if self.instModel == '53230A':
                self.inst.write('ABOR') # Abort (=quit) measuring if any exists.
                self.inst.write('*RST') # Reset
                self.inst.write('*CLS') # Clear the Status Byte Register
                self.inst.write('DATA:POIN:EVEN:THR 1') #' + self.config['READCNT']) # Measurement count threshold is set to 1.
                self.inst.write('STAT:OPER:ENAB 4096') # Relation between the event and Standard Operation Register. (If measurement count exceed the threshold, SOR is turned on.)
                self.inst.write('*SRE 128') # Relation between the Status Byte Register and RQS (6th bit of SBR).
                self.inst.write('ROSC:SOUR:AUTO ON') # Reference oscillator is automatically selected.
                #self.inst.write('SYST:TIM 10')

                if self.config['CONF'] == 'FREQ':
                    self.inst.write(f"CONF:{self.config['CONF']} (@{self.config['CHAN']}")
                elif self.config['CONF'] == 'TINT':
                    self.inst.write(f"CONF:{self.config['CONF']} (@{self.config['CHAN'][0]}),(@{self.config['CHAN'][-1]})")
                else:
                    self.inst.write(f"CONF:{self.config['CONF']}")

                self.inst.write('INP1:COUP ' + self.config['COUP1'])
                self.inst.write('INP2:COUP ' + self.config['COUP2'])
                if self.config['IMP1'] == 'HIGH' or self.config['IMP1'] == '1M':
                    self.config['IMP1'] = '1E6'
                self.inst.write('INP1:IMP ' + self.config['IMP1'])
                if self.config['IMP2'] == 'HIGH' or self.config['IMP2'] == '1M':
                    self.config['IMP2'] = '1E6'
                self.inst.write('INP2:IMP ' + self.config['IMP2'])
                self.inst.write('INP1:LEV ' + self.config['LEV1'])
                self.inst.write('INP2:LEV ' + self.config['LEV2'])
                self.inst.write('INP1:SLOP ' + self.config['SLO1'])
                self.inst.write('INP2:SLOP ' + self.config['SLO2'])
                self.inst.write('TRIG:COUN 1E6') # Set as maximum
                self.inst.write('SAMP:COUN 1E6') # Set as maximum

            elif self.instModel == '53132A' or self.instModel == '53131A':
                self.inst.write('ABOR') # Abort (=quit) measuring if any exists.
                self.inst.write('*RST') # Reset
                self.inst.write('*CLS') # Clear the Status Byte Register
                self.inst.write(':STAT:PRESet')
                self.inst.write(':STAT:OPER:PTR 0; NTR 16') # Rule for detecting a negative transition (?)
                self.inst.write(':STAT:OPER:ENAB 16') # Masking Operation Status Register to represent 4th bit(Measuring) only.
                self.inst.write('*SRE 128')

                self.inst.write('ROSC:SOUR:AUTO ON') # Reference oscillator is automatically selected.
                self.inst.write('CONF:' + self.config['CONF'])
                self.inst.write('INP1:COUP ' + self.config['COUP1'])
                self.inst.write('INP2:COUP ' + self.config['COUP2'])
                if self.config['IMP1'] == 'HIGH' or self.config['IMP1'] == '1M': self.config['IMP1'] = '1E6'
                self.inst.write('INP1:IMP '+self.config['IMP1'])
                if self.config['IMP2'] == 'HIGH' or self.config['IMP2'] == '1M': self.config['IMP2'] = '1E6'
                self.inst.write('INP2:IMP '+self.config['IMP2'])
                self.inst.write('SENS:EVEN1:LEV:AUTO OFF')
                self.inst.write('SENS:EVEN2:LEV:AUTO OFF')
                self.inst.write('SENS:EVEN1:LEV ' + self.config['LEV1'])
                self.inst.write('SENS:EVEN2:LEV ' + self.config['LEV2'])
                self.inst.write('SENS:EVEN1:SLOP ' + self.config['SLO1'])
                self.inst.write('SENS:EVEN2:SLOP ' + self.config['SLO2'])

            elif self.instModel == 'SR620':
                self.inst.write('*RST')
                self.inst.write('*CLS')
                self.inst.write('TENA 4')
                self.inst.write('SIZE 1')
                self.inst.write('SRCE 0')
                self.inst.write('*SRE 8')

                if self.config['CONF'] == 'TINT':
                    self.inst.write('MODE 0')
                if self.config['COUP1'] == 'DC': self.inst.write('TCPL 1, 0')
                elif self.config['COUP1'] == 'AC': self.inst.write('TCPL 1, 1')
                else: raise Exception
                if self.config['COUP2'] == 'DC': self.inst.write('TCPL 2, 0')
                elif self.config['COUP2'] == 'AC': self.inst.write('TCPL 2, 1')
                else: raise Exception
                if self.config['IMP1'] == '50': self.inst.write('TERM 1, 0')
                elif self.config['IMP1'] == '1E6' or self.config['IMP1'] == 'HIGH' or self.config['IMP1'] == '1M': self.inst.write('TERM 1, 1')
                else: raise Exception
                if self.config['IMP2'] == '50': self.inst.write('TERM 2, 0')
                elif self.config['IMP1'] == '1E6' or self.config['IMP1'] == 'HIGH' or self.config['IMP1'] == '1M': self.inst.write('TERM 2, 1')
                else: raise Exception
                self.inst.write('LEVL 1, ' + self.config['LEV1'])
                self.inst.write('LEVL 2, ' + self.config['LEV2'])
                if self.config['SLO1']=='POS': self.inst.write('TSLP 1,0')
                elif self.config['SLO1']=='NEG': self.inst.write('TSLP 1, 1')
                else: raise Exception
                if self.config['SLO2']=='POS': self.inst.write('TSLP 2,0')
                elif self.config['SLO2']=='NEG': self.inst.write('TSLP 2, 1')
                else: raise Exception

            else:
                logger.error('@applyOptions: Unexpected model name.')
                return False
            return True
        except:
            logger.error('@applyOptions: Problem occured while reading .ini file.')
            return False

    ## INITIATE MEASURING
    def start(self):
        try:
            self.flag_start = False
            if self.instModel == '53230A':
                self.inst.write('INIT')
                self.flag_start = True
            elif self.instModel == '53132A' or self.instModel == '53131A':
                self.inst.write('INIT:CONT ON')
                self.flag_start = True
            elif self.instModel == 'SR620':
                self.flag_start = True
            else:
                logger.error('@start: Unexpected model name.')
        except:
            logger.error('@start: Failed to start ' + self.instModel +'.')
        return self.flag_start

    ## CHECK REGISTERS AND DO TASKS
    def check(self, reg_prev):
        if self.instModel == '53230A':
            stb = format(self.inst.stb, '08b')
            logger.debug('@check: STB is ' + stb)

            if stb[0] == '1' or True:# Number of the measurements is reached to the threshold (=READCNT).
                logger.debug('@check: STB[0] detected. (Measurement queue)')
                self.send_CLS()
                self.send_R()
                stb0 = True
            else:
                stb0 = False
            if stb[5] == '1': # Errors exist.
                logger.debug('@check: STB[5] detected. (Error queue)')
                self.send_CLS()
                self.send_ERR()
                stb5 = True
            else:
                stb5 = False
                
            reg_prev = self.comp_reg(reg_prev, stb)
            
            if (not stb0) and (not stb5):
                logger.debug('@check: No STB detected.')
                self.missed += 1
                if self.missed > 2:
                    pass#print('PAUSE!')
            else:
                self.missed = 0

        elif self.instModel == '53132A' or self.instModel == '53131A':
            stb = format(self.inst.stb, '08b')
            if stb[0] == '1':
                logger.debug('@check: STB[0] detected. (Measurement queue)')
                self.send_DATA()
                self.send_CLS()
            else:
                logger.debug('@check: No STB detected.')

        elif self.instModel == 'SR620':
            stb = format(self.inst.stb, '08b')
            if stb[4] == '1':
                logger.debug('@check: STB[4] detected. (Measurement queue)')
                self.send_XAVG()
                self.send_CLS()
            else:
                logger.debug('@check: No STB detected.')
        else:
            logger.error('@check: Unexpected model name.')
        return True, reg_prev

    def comp_reg(self, reg_prev, stb):
        reg_STB = f"{int(self.inst.query('*STB?')[1:-1]):b}".zfill(8)
        reg_SRE = f"{int(self.inst.query('*SRE?')[1:-1]):b}".zfill(8)
        #reg_ERR = self.inst.query('SYST:ERR?')[1:-1]
        reg_QCOND = f"{int(self.inst.query('STAT:QUES:COND?')[1:-1]):b}".zfill(16)
        reg_QEVEN = f"{int(self.inst.query('STAT:QUES:EVEN?')[1:-1]):b}".zfill(16) #'xxxxxxxxxxxxxxxx' #
        reg_QENAB = f"{int(self.inst.query('STAT:QUES:ENAB?')[1:-1]):b}".zfill(16)
        reg_ESR = f"{int(self.inst.query('*ESR?')[1:-1]):b}".zfill(8)
        reg_ESE = f"{int(self.inst.query('*ESE?')[1:-1]):b}".zfill(8)
        reg_OCOND = f"{int(self.inst.query('STAT:OPER:COND?')[1:-1]):b}".zfill(16)
        reg_OEVEN = 'xxxxxxxxxxxxxxxx' #f"{int(self.inst.query('STAT:OPER:EVEN?')[1:-1]):b}".zfill(16)
        reg_OENAB = f"{int(self.inst.query('STAT:OPER:ENAB?')[1:-1]):b}".zfill(16)
        reg = f'|{stb} {reg_STB} {reg_SRE}|{reg_QCOND} {reg_QEVEN} {reg_QENAB}|{reg_ESR} {reg_ESE}|{reg_OCOND} {reg_OEVEN} {reg_OENAB}|'
        
        if reg != reg_prev:
            logger.info('|stb      STB      SRE     | STAT:QUES:COND  EVEN             ENAB            |ESR      ESE     |STAT:OPER:COND   EVEN             ENAB            |')
            logger.info(reg)
            #logger.debug('@check: STB is changed. ')
            idx_str = list(''.ljust(149))
            for i in [x for x in range(len(reg)) if reg[x] != reg_prev[x]]:
                idx_str[i] = '^'
            logger.info(''.join(idx_str))
            
        return reg
    
    ## SEND A QUERY OR AN INSTRUCTION AND TREAT THE ANSWERS APPROPRIATELY
    def send_R(self):
        fileName = 'DATA/MEAS_'+self.instID+'_'+datetime.utcnow().strftime('%y%m%d')+'.txt'
        if not os.path.exists(os.path.dirname(fileName)):
            os.makedirs(os.path.dirname(fileName))
        
        with open(fileName, 'a+') as f:
            if os.stat(fileName).st_size == 0:
                self.write_header(f)
            logger.info('> Sent an R? query to ' + self.instID + ' on:    ' + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
            ans = self.inst.query('R?') # 데이터 쿼리 요청
            t_rcv = datetime.utcnow()
            if ans[0] == '#':
                logger.info('< Received an answer from ' + self.instID + ' on: ' + t_rcv.strftime('%y/%m/%d %H:%M:%S.%f'))
                if '#10' not in ans:
                    logger.info('* Return from ' + self.instID + ' = ' + ans[:100])#ans[:-1])
                    N_comma = ans.count(',')
                    if self.timestamp == 'SUP':
                        f.write(date2mjd(t_rcv.strftime('%Y'), t_rcv.strftime('%m'), t_rcv.strftime('%d')) + ' ' + t_rcv.strftime('%H:%M:%S') + ' ' + t_rcv.strftime('%f')[0:2] + ' ') # 리턴 시각 기록
                        for i in range(N_comma):
                            ans = ans[ans.find(',')+1:]
                        lastOne = ans[ans.find('+'):ans.find('E')+5]
                        f.write(lastOne + '\n')
                    else:
                        for i in range(N_comma+1):
                            t_write = t_rcv + timedelta(seconds = i-N_comma)
                            if self.timestamp == 'DUP':
                                f.write(date2mjd(t_rcv.strftime('%Y'), t_rcv.strftime('%m'), t_rcv.strftime('%d')) + ' ' + t_rcv.strftime('%H:%M:%S') + ' ' + t_rcv.strftime('%f')[0:2] + ' ') # 리턴 시각 기록
                            elif self.timestamp == 'SER':
                                f.write(date2mjd(t_write.strftime('%Y'), t_write.strftime('%m'), t_write.strftime('%d')) + ' ' + t_write.strftime('%H:%M:%S') + ' ' + t_rcv.strftime('%f')[0:2] + ' ') # 리턴 시각 기록
                            firstOne = ans[ans.find('+'):ans.find('E')+5]
                            #f.write(firstOne+' [' +t_rcv.strftime('%H:%M:%S %f')[:-4]+', ' + str(N_comma+1) + ']\n') # 리턴 내용 기록
                            f.write(firstOne + '\n')
                            ans = ans[ans.find(',')+1:]
                else:
                    logger.warning('* Return from ' + self.instID + ' is empty.')
            else:
                logger.warning('< Received unexpected answer on:'+ t.strftime('%y/%m/%d %H:%M:%S.%f'))

    def send_ERR(self):
        while format(self.inst.stb, '08b')[5] == '1':
                logger.info('> Sent an ERR? query on: ' + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
                errStr = self.inst.query('SYST:ERR?')[:-1] # 에러 쿼리 요청
                logger.info('< Received an answer on: ' + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
                logger.error('* ERROR message from the instrument [' + self.instID + '] ' + errStr)

    def send_CLS(self):
        self.inst.write('*CLS')
        logger.info('> Sent *CLS instruction to ' + self.instID + ' on: '  + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
        # while format(self.inst.stb, '08b')[1] == '1':
        #     pass

    def send_DATA(self):
        fileName = 'DATA/MEAS_'+self.instID+'_'+datetime.utcnow().strftime('%y%m%d')+'.txt'
        if not os.path.exists(os.path.dirname(fileName)):
            os.makedirs(os.path.dirname(fileName))
        with open(fileName,'a+') as f:
            if os.stat(fileName).st_size == 0:
                self.write_header(f)
            logger.info('> Sent an DATA? query to ' + self.instID + ' on: ' + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
            ans = self.inst.query('DATA?') # 데이터 쿼리 요청
            t_rcv = datetime.utcnow()
            logger.info('< Received an answer from ' + self.instID + ' on: ' + t_rcv.strftime('%y/%m/%d %H:%M:%S.%f'))
            logger.info('* Return from ' + self.instID + ' = ' + ans[:-1])
            f.write(date2mjd(t_rcv.strftime('%Y'), t_rcv.strftime('%m'), t_rcv.strftime('%d')) + ' ' + t_rcv.strftime('%H:%M:%S') + ' ' + t_rcv.strftime('%f')[0:2] + ' ') # 리턴 시각 기록
            f.write(ans[ans.find('+'):ans.find('E')+5]+'\n') # 리턴 내용 기록

    def send_XAVG(self):
        fileName = 'DATA/MEAS_'+self.instID+'_'+datetime.utcnow().strftime('%y%m%d')+'.txt'
        if not os.path.exists(os.path.dirname(fileName)):
            os.makedirs(os.path.dirname(fileName))
        with open(fileName,'a+') as f:
            if os.stat(fileName).st_size == 0:
                self.write_header(f)
            logger.info('> Sent an XAVG? query to ' + self.instID + ' on: ' + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
            ans = self.inst.query('XAVG?') # 데이터 쿼리 요청
            t_rcv = datetime.utcnow()
            logger.info('< Received an answer from ' + self.instID + ' on: ' + t_rcv.strftime('%y/%m/%d %H:%M:%S.%f'))
            logger.info('* Return from ' + self.instID + ' = ' + ans[:-1])
            f.write(date2mjd(t_rcv.strftime('%Y'), t_rcv.strftime('%m'), t_rcv.strftime('%d')) + ' ' + t_rcv.strftime('%H:%M:%S') + ' ' + t_rcv.strftime('%f')[0:2] + ' ') # 리턴 시각 기록
            f.write(ans[:-1]+'\n') # 리턴 내용 기록

    def send_raiseErr(self):
        print('************* Sent an ERROR query! *****************')
        try:
            self.inst.query('RAISE_ERROR?')
        except:
            pass
        logger.info('* RAISED AN INTENTIONAL ERROR.')

    def write_header(self, f):
        f.write('<GPIB LOGGER OUTPUT>\n')
        datestr = datetime.utcnow().strftime('%Y%m%d')
        f.write('Date = ' + datestr + ' (UTC)\n')
        f.write('MJD = ' + date2mjd(datestr[0:4], datestr[4:6], datestr[6:8]) + '\n')
        f.write('DOY = ' + str(datetime.utcnow().timetuple().tm_yday) + '\n')
        f.write('TimeTag = UTC\n')
        f.write('FILE_ID = ' + self.config['FILE_ID'] + '\n')
        f.write('IDN = ' + self.inst.query('*IDN?'))
        f.write('Configuration = ' + self.config['CONF']+'\n')
        f.write('Ch1 = '+self.config['COUP1']+' / '+self.config['IMP1']+' / '+self.config['LEV1']+' / '+self.config['SLO1']+'\n')
        f.write('Ch2 = '+self.config['COUP2']+' / '+self.config['IMP2']+' / '+self.config['LEV2']+' / '+self.config['SLO2']+'\n')
        f.write('\n')
        f.write('MJD HH:mm:ss MEASUREMENT\n')

def make_logger():
    logger = logging.getLogger(None)

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(lineno)s - %(levelname)s - %(message)s')
    
    console = logging.StreamHandler()

    current_dir = os.path.dirname(os.path.realpath(__file__))
    log_dir = '{}/LOG'.format(current_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    LOG_FILENAME = 'LOG/log'
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=LOG_FILENAME, when='midnight',interval=1, encoding='utf-8', utc=True)
    file_handler.suffix = '%y%m%d.log'

    console.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger

def initInst():
    MyInst = []
    ## LOAD .ini FILE
    INI_NAME = os.path.abspath( __file__ )[:-3] + '.ini'
    if os.path.exists(INI_NAME):
        config = configparser.ConfigParser()
        config.read(INI_NAME)
        N_SECTION = len(config.sections())-1
    else:
        logger.error(f'@initInst: {INI_NAME} is not found.')
        return (None, [], None)

    ## GENERAL OPTION : SELECT INSTRUMENTS
    if config.has_option('GENERAL_OPTIONS', 'SELECT_INST'):
        sel_list_opt = config.get('GENERAL_OPTIONS', 'SELECT_INST')
        if sel_list_opt == 'ALL':
            sel_list = [format(x, 'd') for x in range(N_SECTION)]
        else:
            sel_list = sel_list_opt.split(',')
            for i in sel_list:
                if config.has_section(f'INST{i}'):
                    pass
                else:
                    logger.error('@initInst: SELECT_INST option in .ini file does not match with the section names.')
                    return (None, [], None)
    else:
        logger.info('@initInst: No SELECT_INST option in .ini file. Set ALL as a default.')
        sel_list = [format(x, 'd') for x in range(N_SECTION)]

    ## GENERAL OPTION : SET LOG LEVEL
    if config.has_option('GENERAL_OPTIONS', 'LOG_LEVEL'):
        log_level_opt = config.get('GENERAL_OPTIONS', 'LOG_LEVEL')
        if any(log_level_opt in s for s in ['DEBUG', 'INFO','WARNING','ERROR','CRITICAL']): # Check the input is one of the expected.
            for handler in logger.handlers:
                handler.setLevel(log_level_opt)
        else:
            logger.info('@initInst: Unexpected LOG_LEVEL option in .ini file. Set INFO as a default.')
    else:
        logger.warning('@initInst: No LOG_LEVEL option in .ini file. Set INFO as a default.')

    ## GENERAL OPTION : SET QUERY INTERVAL
    if config.has_option('GENERAL_OPTIONS', 'QUERY_INTERVAL'):
        qint = float(config.get('GENERAL_OPTIONS', 'QUERY_INTERVAL'))
    else:
        qint = 0
        logger.info('@initInst: No QUERY_INTERVAL option in .ini file. Set 0 as a default.')

    ## INITIALIZE INSTRUMENTS
    for i in range(int(N_SECTION)): # SECTION NUMBERS HAVE TO BE SERIAL.
        if str(i) in sel_list:
            MyInst.append(Instrument(config,i))
            if MyInst[-1].flag_init is False:
                logger.error(f'@initInst: Failed to initialize MyInst[{str(i)}].')
            else:
                if MyInst[-1].start() is False:
                    logger.error(f'@initInst: Failed to start MyInst[{str(i)}].')
        else:
            MyInst.append(None)
    return (MyInst, sel_list, qint)

def measInst(MyInst, sel_list, qint):
    try:
        cnt_serial_failures = 0
        t = TicToc()
        t.tic()
        logger.debug('@measInst: Measurement loop is started.')
        reg_prev = ''.rjust(149)

        while True:
            #logger.info('====================================================================================================================================================')
            reg_prev = MyInst[0].comp_reg(reg_prev, format(MyInst[0].inst.stb, '08b'))
            if t.tocvalue() > qint:
                logger.debug('@measInst: Measurement loop is started.')
                t.tic()
                for i in sel_list:
                    if MyInst[int(i)] is not None and MyInst[int(i)].flag_start:
                        flag_OK, reg_prev = MyInst[int(i)].check(reg_prev)
                        cnt_serial_failures = 0
                    else:
                        cnt_serial_failures += 1
                        logger.critical('@measInst: MyInst[' + i + '] is not working. (' + str(cnt_serial_failures) + ' serial failures)')
                        if cnt_serial_failures >= 1000:
                            raise SystemExit
            else:
                pass

    except (KeyboardInterrupt, SystemExit):
        if cnt_serial_failures > 1000:
            logger.info('@measInst: Program is terminated because over 1000 serial failures occured.')
        else:
            logger.info('@measInst: Program is terminated by an external keyboard input.')

## MAIN FUNCTION
if __name__ == '__main__':
    ## Make a logger
    logger = make_logger()

    ## Initiate instruments and start measuring
    (MyInst, sel_list, qint) = initInst()

    ## Eternal loop that checks STB and saves measurements
    if all(x.inst is None for x in MyInst):
        logger.error('@initInst: All instruments are not available.')
    else:
        measInst(MyInst, sel_list, qint)
    print('Done')