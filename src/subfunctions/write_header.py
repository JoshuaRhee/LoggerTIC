from datetime import datetime
from subfunctions.date2mjd import date2mjd

def write_header(myInst, f):
    f.write('<GPIB LOGGER OUTPUT>\n')
    datestr = datetime.utcnow().strftime('%Y%m%d')
    f.write('Date = ' + datestr + ' (UTC)\n')
    f.write('MJD = ' + date2mjd(datestr[0:4], datestr[4:6], datestr[6:8]) + '\n')
    f.write('DOY = ' + str(datetime.utcnow().timetuple().tm_yday) + '\n')
    f.write('TimeTag = UTC\n')
    f.write('File ID = ' + myInst.config['FILE_ID'] + '\n')
    f.write('Device IDN = ' + myInst.inst.query('*IDN?'))
    f.write('Connection = ' + myInst.config['INTERFACE'] + ' ' + myInst.config['ADDRESS'] + '\n')
    #if myInst.conf['CONF'] exists & myInst.conf['CHAN'] exists?
    f.write('Configuration = ' + myInst.config['CONF'] + ' ' + myInst.config['CHAN'] + '\n')
    # if myInst.config['COUP1'] ?
    # str += myInst.config['COUP1']
    # if str:
    # f.write('Ch1 = ' + str)
    # Do same for ch2
    f.write('Ch1 = '+myInst.config['COUP1']+' / '+myInst.config['IMP1']+' / '+myInst.config['LEV1']+' / '+myInst.config['SLO1']+'\n')
    f.write('Ch2 = '+myInst.config['COUP2']+' / '+myInst.config['IMP2']+' / '+myInst.config['LEV2']+' / '+myInst.config['SLO2']+'\n')
    f.write('\n')
    f.write('MJD HH:mm:ss MEASUREMENT\n')