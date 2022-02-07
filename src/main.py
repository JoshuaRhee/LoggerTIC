#######################################
# Time Interval Counter Logger
# Device: 53230A, 53131A, 53132A, SR620
# Version: 1.7
# Additional instructions in apply_presets
# Tested on 15 devices at once
#######################################

import configparser
from datetime import datetime, timedelta
from subfunctions.apply_presets import apply_presets
from subfunctions.date2mjd import date2mjd
from subfunctions.make_logger import make_logger
import os
from pytictoc import TicToc
import pyvisa

class Instrument:
    def __init__(self, config_section, numInst):
        self.missed = 0
        self.flag_init = False
        self.flag_infinite = False
        self.config_section = config_section
        if config_section.has_section('INST'+str(numInst)):
            self.config = config_section['INST'+str(numInst)]
            self.inst = self.connect_inst(numInst)
            if self.inst:
                if self.apply_options(numInst):
                    self.flag_init = True
                else:
                    pass
            else:
                logger.error(f'@__init__: Both GPIB and TCPIP connection were failed for [INST{str(numInst)}].')
        else:
            pass

    ## CONNECT TO THE INSTRUMENT
    def connect_inst(self, numInst):
        if not self.config_section.has_option('INST'+str(numInst), 'INTERFACE'):
            logger.error('@connect_inst: There is no INTERFACE option in section [INST' + str(numInst) + '].')
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
                    logger.info(f'@connect_inst: Connect to TCPIP ({IPaddr}).')
                    return Instrument
                except:
                    logger.error(f'@connect_inst: Failed to connect to TCP/IP ({IPaddr}).')
                    return None
            elif self.config['INTERFACE'] == 'TCPIP_SOCKET':
                return None
            elif self.config['INTERFACE'] == 'GPIB_INSTR':
                for i in range(3):
                    try:
                        GPIBaddr = self.config['ADDRESS']
                        rm = pyvisa.ResourceManager()
                        rm.list_resources()
                        (f'GPIB0::{GPIBaddr}::INSTR')
                        Instrument = rm.open_resource(f'GPIB0::{GPIBaddr}::INSTR')
                        self.instModel = Instrument.query('*IDN?').split(',')[1]
                        logger.info(f'@connect_inst: Connected to GPIB ({GPIBaddr}).')
                        return Instrument
                    except:
                        pass
                logger.error(f'@connect_inst: Failed to connect to GPIB ({GPIBaddr}). Trial [{str(i+1)}/3].')
                return None
            elif self.config['INTERFACE'] == 'SERIAL_INSTR':
                return None
            elif self.config['INTERFACE'] == 'ENET-SERIAL_INSTR':
                return None
            else:
                logger.error('@connect_inst: INTERFACE option is not appropriate.')
                return None

    ## APPLY PRESET OPTIONS
    def apply_options(self, numInst):
        try:
            # Check FILE_ID option
            if self.config_section.has_option('INST'+str(numInst), 'FILE_ID'):
                self.instID = self.config['FILE_ID']
            else:
                logger.error(f'@apply_options: There is no FILE_ID option in a section [INST{str(numInst)}].')
                return False

            # Check TIMESTAMP option
            if self.config_section.has_option('INST'+str(numInst), 'TIMESTAMP'):
                self.timestamp = self.config['TIMESTAMP']
                if self.timestamp not in ['SUP','DUP','SER']:
                    self.timestamp='DUP'
                    logger.warning('@apply_options: Improper TIMETAG option in .ini file. Set DUP as a default.')
            else:
                self.timestamp='SUP'
                logger.warning('@apply_options: No TIMESTAMP option in .ini file. Set SUP as a default.')

            # Apply other specific options with queries
            return_apply_presets = apply_presets(self)
            if return_apply_presets == 'Done':
                return True
            else:
                logger.error('@apply_presets: ' + return_apply_presets)
                return False
        except:
            logger.error('@apply_options: Problem occured while reading .ini file.')
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
    def check(self, cnt_check):
        if self.instModel == '53230A':
            reg_to_check = format(int(self.inst.query('STAT:OPER:COND?')[1:-1]), '016b')
            logger.debug('@check: STAT:OPER:COND is ' + reg_to_check)

            if reg_to_check[-13] == '1':# or True # Number of the measurements is reached to the threshold (=READCNT).
                logger.debug('@check: STAT:OPER:COND[-13] is detected.')
                self.send_CLS()
                #self.send_READ()
                self.send_R()
                if self.flag_infinite is True and cnt_check > 9E5:
                    self.inst.write('ABOR')
                    self.inst.write('INIT')
                    logger.info('@check: Device is re-initialized for the infinite mode.')
                    return True, True
                return True, False
            else:
                pass
            # if stb[5] == '1': # Errors exist.
            #     logger.debug('@check: STB[5] detected. (Error queue)')
            #     self.send_CLS()
            #     self.send_ERR()
            #     stb5 = True
            # else:
            #     stb5 = False
                
            # if (not stb0) and (not stb5):
            #     logger.debug('@check: No STB detected.')
            #     self.missed += 1
            #     if self.missed > 30:
            #         pass#print('PAUSE!')
            # else:
            #     self.missed = 0

        elif self.instModel == '53132A' or self.instModel == '53131A':
            stb = format(self.inst.stb, '08b')
            if stb[0] == '1':
                logger.debug('@check: STB[0] detected. (Measurement queue)')
                self.send_DATA()
                self.send_CLS()
                return True, False
            else:
                logger.debug('@check: No STB detected.')

        elif self.instModel == 'SR620':
            stb = format(self.inst.stb, '08b')
            #print(str(stb))
            if stb[7] == '0':
                #logger.debug('@check: STB[3] detected. (Measurement queue)')
                logger.debug('@check: STB[7] == 0 detected. (READY:No meas are in progress)')
                self.send_XAVG()
                self.send_CLS()
                return True, False
            else:
                logger.debug('@check: No STB detected.')
        else:
            logger.error('@check: Unexpected model name.')
        return False, False

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
        fileName = 'outputs/measurements/MEAS_'+self.instID+'_'+datetime.utcnow().strftime('%y%m%d')+'.txt'
        with open(fileName, 'a+') as f:
            logger.info('> Sent an R? query to ' + self.instID + ' on:    ' + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
            ans = self.inst.query('R?') # 데이터 쿼리 요청
            t_rcv = datetime.utcnow()
            if ans[0] == '#':
                logger.info('< Received an answer from ' + self.instID + ' on: ' + t_rcv.strftime('%y/%m/%d %H:%M:%S.%f'))
                if '#10' not in ans:
                    if len(ans) > 100:
                        logger.info('* Return from ' + self.instID + ' = ' + ans[:95] + ' ... ')#ans[:-1])
                    else:
                        logger.info('* Return from ' + self.instID + ' = ' + ans[:-1])#ans[:-1])
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
                logger.warning('< Received unexpected answer on:'+ t_rcv.strftime('%y/%m/%d %H:%M:%S.%f'))

    def send_READ(self):
        fileName = 'outputs/measurements/MEAS_'+self.instID+'_'+datetime.utcnow().strftime('%y%m%d')+'.txt'
        with open(fileName, 'a+') as f:
            logger.info('> Sent an READ? query to ' + self.instID + ' on:    ' + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
            ans = self.inst.query('READ?') # 데이터 쿼리 요청
            t_rcv = datetime.utcnow()
            #if ans[0] == '#':
            logger.info('< Received an answer from ' + self.instID + ' on: ' + t_rcv.strftime('%y/%m/%d %H:%M:%S.%f'))
            logger.info('* Return from ' + self.instID + ' = ' + ans[:-1])
            f.write(date2mjd(t_rcv.strftime('%Y'), t_rcv.strftime('%m'), t_rcv.strftime('%d')) + ' ' + t_rcv.strftime('%H:%M:%S') + ' ' + t_rcv.strftime('%f')[0:2] + ' ') # 리턴 시각 기록
            f.write(ans[ans.find('+'):ans.find('E')+5]+'\n') # 리턴 내용 기록
            #else:
            #    logger.warning('< Received unexpected answer on:'+ t_rcv.strftime('%y/%m/%d %H:%M:%S.%f'))

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
        fileName = 'outputs/measurements/MEAS_'+self.instID+'_'+datetime.utcnow().strftime('%y%m%d')+'.txt'
        with open(fileName,'a+') as f:
            logger.info('> Sent an DATA? query to ' + self.instID + ' on: ' + datetime.utcnow().strftime('%y/%m/%d %H:%M:%S.%f'))
            ans = self.inst.query('DATA?') # 데이터 쿼리 요청
            t_rcv = datetime.utcnow()
            logger.info('< Received an answer from ' + self.instID + ' on: ' + t_rcv.strftime('%y/%m/%d %H:%M:%S.%f'))
            logger.info('* Return from ' + self.instID + ' = ' + ans[:-1])
            f.write(date2mjd(t_rcv.strftime('%Y'), t_rcv.strftime('%m'), t_rcv.strftime('%d')) + ' ' + t_rcv.strftime('%H:%M:%S') + ' ' + t_rcv.strftime('%f')[0:2] + ' ') # 리턴 시각 기록
            f.write(ans[ans.find('+'):ans.find('E')+5]+'\n') # 리턴 내용 기록

    def send_XAVG(self):
        fileName = 'outputs/measurements/MEAS_'+self.instID+'_'+datetime.utcnow().strftime('%y%m%d')+'.txt'
        with open(fileName,'a+') as f:
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
            sel_section_list = [x for x in range(N_SECTION)]
        else:
            sel_id_list = sel_list_opt.split(',')
            sel_section_list = []
            for sel_id in sel_id_list:
                for section_name in config.sections()[1:]:
                    if sel_id == config.get(section_name, 'FILE_ID'):
                        sel_section_list.append(int(section_name[4:]))
                    else:
                        pass
            if len(sel_id_list) != len(sel_section_list):
                logger.error('@initInst: Some FILE_ID in the SELECT_INST option in .ini file does not match to any section.')
                return (None, [], None)
            else:
                pass
    else:
        logger.info('@initInst: No SELECT_INST option in .ini file. Set ALL as a default.')
        sel_section_list = [x for x in range(N_SECTION)]

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
        if i in sel_section_list:
            MyInst.append(Instrument(config,i))
            if MyInst[-1].flag_init is False:
                logger.error(f'@initInst: Failed to initialize MyInst[{str(i)}].')
                #return ([], sel_section_list, qint)
            else:
                if MyInst[-1].start() is False:
                    logger.error(f'@initInst: Failed to start MyInst[{str(i)}].')
                    #return ([], sel_section_list, qint)
        else:
            MyInst.append(None)
    return (MyInst, sel_section_list, qint)

def measInst(MyInst, sel_section_list, qint):
    try:
        cnt_check = 1
        cnt_first = 1
        cnt_serial_failures = 0
        t = TicToc()
        t.tic()
        logger.debug('@measInst: Measurement loop is started.')
        
        while True:
            if t.tocvalue() > qint or cnt_first == 1:
                logger.debug('@measInst: Measurement loop is started.')
                t.tic()
                for i in sel_section_list:
                    if MyInst[i].inst is not None:
                        if MyInst[i].flag_start:
                            flag_OK, flag_reset_cnt = MyInst[i].check(cnt_check)
                            if flag_OK:
                                cnt_first = 0
                                cnt_check += 1
                            if flag_reset_cnt:
                                cnt_check = 1
                                cnt_first = 1
                            cnt_serial_failures = 0
                        else:
                            logger.critical('@measInst: MyInst[' + str(i) + '] is not working. (' + str(cnt_serial_failures) + ' serial failures)')
                    else:
                        cnt_serial_failures += 1
                        logger.critical('@measInst: MyInst[' + str(i) + '] is not working. (' + str(cnt_serial_failures) + ' serial failures)')
                        if cnt_serial_failures >= 10:
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
    (MyInst, sel_section_list, qint) = initInst()

    ## Eternal loop that checks STB and saves measurements
    if all(x is None for x in MyInst):
        logger.error('@initInst: Measurement is not started due to the fail in initialization.')
    else:
        measInst(MyInst, sel_section_list, qint)
    print('Done')