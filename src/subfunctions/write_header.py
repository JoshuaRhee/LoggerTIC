from datetime import datetime
from subfunctions.date2mjd import date2mjd
import os

def write_header(myInst):
    fileName = 'outputs/measurements/MEAS_'+myInst.instID+'_'+datetime.utcnow().strftime('%y%m%d')+'.txt'
    if not os.path.exists(os.path.dirname(fileName)):
        os.makedirs(os.path.dirname(fileName))
        
    with open(fileName, 'a+') as f:
        if os.stat(fileName).st_size == 0:
            f.write('<GPIB LOGGER OUTPUT>\n')
            f.write('Reference Time = UTC\n')
            datestr = datetime.utcnow().strftime('%Y-%m-%d')
            f.write('Date = ' + datestr + '\n')
            f.write('MJD/DOY = ' + date2mjd(datestr[0:4], datestr[5:7], datestr[8:10]) + '/' + str(datetime.utcnow().timetuple().tm_yday) +'\n')
            f.write('File ID = ' + myInst.config['FILE_ID'] + '\n')
            f.write('Device Model = ' + myInst.instModel + '\n')
            f.write('Connect/Port = ' + myInst.config['INTERFACE'] + '/' + myInst.config['ADDRESS'] + '\n')
            f.write(myInst.str_header)
            f.write('\n')
            f.write('MJD   HH:mm:ss.ss MEASUREMENT\n')
        else:
            pass
    return True