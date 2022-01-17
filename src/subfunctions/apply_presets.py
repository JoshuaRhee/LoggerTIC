from datetime import datetime
from subfunctions.date2mjd import date2mjd
import os

def apply_presets(myInst):
    str_header = ''
    
    if myInst.instModel == '53230A':
        myInst.inst.write('ABOR') # Abort (=quit) measuring if any exists.
        myInst.inst.write('*RST') # Reset
        myInst.inst.write('*CLS') # Clear the Status Byte Register
        myInst.inst.write('DATA:POIN:EVEN:THR 1') #' + inst.config['READCNT']) # Measurement count threshold is set to 1.
        myInst.inst.write('STAT:OPER:ENAB 4096') # Relation between the event and Standard Operation Register. (If measurement count exceed the threshold, SOR is turned on.)
        myInst.inst.write('*SRE 128') # Relation between the Status Byte Register and RQS (6th bit of SBR).
        myInst.inst.write('ROSC:SOUR:AUTO ON') # Reference oscillator is automatically selected.
        myInst.inst.write('SYST:TIMeout INF')

        if not myInst.config_section.has_option(myInst.config.name, 'CONF'):
            return 'There is no CONF option in section ' + myInst.config.name

        if myInst.config['CONF'] == 'FREQ':
            if not myInst.config_section.has_option(myInst.config.name, 'CHAN'):
                return 'There is no CHAN option in section ' + myInst.config.name
            else:
                chans = myInst.config['CHAN']
                myInst.inst.write(f"CONF:{myInst.config['CONF']} (@{chans})")
                str_header += 'Configure/Ch = ' + myInst.config['CONF'] + ' ' + myInst.config['CHAN'] + '\n'
                
            # Default gap-free measurements settings from the manual
            myInst.inst.write('TRIG:COUN 1')
            myInst.inst.write('SAMP:COUN 1E6')
            myInst.inst.write('FREQ:MODE CONT')
            myInst.inst.write('SENS:FREQ:GATE:SOUR TIME')
            myInst.inst.write('SENS:FREQ:GATE:TIME 1')
            str_header += 'Meas Setting = Gap-free mode. TRIG:COUN 1/SAMP:COUN 1E6' + '\n'
            
        elif myInst.config['CONF'] == 'TINT':
            if not myInst.config_section.has_option(myInst.config.name, 'CHAN'):
                myInst.inst.write(f"CONF:{myInst.config['CONF']} (@1),(@2)")
                #return 'There is no CHAN option in section ' + myInst.config.name
            else:
                chans = [myInst.config['CHAN'][0], myInst.config['CHAN'][-1]]
                myInst.inst.write(f"CONF:{myInst.config['CONF']} (@{chans[0]}),(@{chans[-1]})")
                str_header += 'Configure/Ch = ' + myInst.config['CONF'] + '/' + myInst.config['CHAN'] + '\n'

            if not myInst.config_section.has_option(myInst.config.name, 'TRIGGER_COUNT'):
                myInst.inst.write(f"TRIG:COUN 1E6")
                trig_coun = '1E6'
                #return 'There is no TRIGGER_COUNT option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"TRIG:COUN {myInst.config['TRIGGER_COUNT']}")
                trig_coun = myInst.config['TRIGGER_COUNT']
                
            if not myInst.config_section.has_option(myInst.config.name, 'SAMPLE_COUNT'):
                myInst.inst.write(f"SAMP:COUN 1E6")
                samp_coun = '1E6'
                #return 'There is no SAMPLE_COUNT option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"SAMP:COUN {myInst.config['SAMPLE_COUNT']}")
                samp_coun = myInst.config['SAMPLE_COUNT']
            str_header += 'Meas Setting = TRIG:COUN ' + trig_coun + '/SAMP:COUN ' + samp_coun + '\n'
        else:
            myInst.inst.write(f"CONF:{myInst.config['CONF']}")

        # if trig_coun == '1E6' and samp_coun == '1E6': should be modified..
        myInst.flag_infinite = True
            
        for chan in chans:
            str_header += 'CH' + chan + '  Setting = '
            if not myInst.config_section.has_option(myInst.config.name, 'COUP'+chan):
                return f'There is no COUP{chan} option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"INP{chan}:COUP {myInst.config['COUP'+chan]}")
                str_header += myInst.config['COUP'+chan]
            
            if not myInst.config_section.has_option(myInst.config.name, 'IMP'+chan):
                return f'There is no IMP{chan} option in section ' + myInst.config.name
            else:
                if myInst.config['IMP'+chan] == 'HIGH' or myInst.config['IMP'+chan] == '1M':
                    myInst.config['IMP'+chan] = '1E6'
                myInst.inst.write(f"INP{chan}:IMP {myInst.config['IMP'+chan]}")
                str_header += '/' + myInst.config['IMP'+chan]
                
            if not myInst.config_section.has_option(myInst.config.name, 'LEV'+chan):
                return f'There is no LEV{chan} option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"INP{chan}:LEV {myInst.config['LEV'+chan]}")
                str_header += '/' + myInst.config['LEV'+chan]
                
            if not myInst.config_section.has_option(myInst.config.name, 'SLO'+chan):
                return f'There is no SLO{chan} option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"INP{chan}:SLOP {myInst.config['SLO'+chan]}")
                str_header += '/' + myInst.config['SLO'+chan]
            str_header += '\n'
            
    elif myInst.instModel == '53132A' or myInst.instModel == '53131A':
        myInst.inst.write('ABOR') # Abort (=quit) measuring if any exists.
        myInst.inst.write('*RST') # Reset
        myInst.inst.write('*CLS') # Clear the Status Byte Register
        myInst.inst.write(':STAT:PRESet')
        myInst.inst.write(':STAT:OPER:PTR 0; NTR 16') # Rule for detecting a negative transition (?)
        myInst.inst.write(':STAT:OPER:ENAB 16') # Masking Operation Status Register to represent 4th bit(Measuring) only.
        myInst.inst.write('*SRE 128')
        myInst.inst.write('ROSC:SOUR:AUTO ON') # Reference oscillator is automatically selected.
        
        if not myInst.config_section.has_option(myInst.config.name, 'CONF'):
            return 'There is no CONF option in section ' + myInst.config.name
        else:
            myInst.inst.write('CONF:' + myInst.config['CONF'])
        if myInst.config['CONF'] == 'FREQ':
            myInst.inst.write(':FREQ:ARM:SOUR IMM')
            myInst.inst.write(':FREQ:ARM:STOP:SOUR TIM')
            myInst.inst.write(':FREQ:ARM:STOP:TIM 1')

        if not myInst.config_section.has_option(myInst.config.name, 'CHAN'):
            return 'There is no CHAN option in section ' + myInst.config.name
        else:
            chans = [myInst.config['CHAN'][0], myInst.config['CHAN'][-1]]
            str_header += 'Configure/Ch = ' + myInst.config['CONF'] + '/' + myInst.config['CHAN'] + '\n'
        
        for chan in chans:
            str_header += 'CH' + chan + '  Setting = '
            if not myInst.config_section.has_option(myInst.config.name, 'COUP'+chan):
                return f'There is no COUP{chan} option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"INP{chan}:COUP {myInst.config['COUP'+chan]}")
                str_header += myInst.config['COUP'+chan]

            if not myInst.config_section.has_option(myInst.config.name, 'IMP'+chan):
                return f'There is no IMP{chan} option in section ' + myInst.config.name
            else:
                if myInst.config['IMP'+chan] == 'HIGH' or myInst.config['IMP'+chan] == '1M':
                    myInst.config['IMP'+chan] = '1E6'
                myInst.inst.write(f"INP{chan}:IMP {myInst.config['IMP'+chan]}")
                str_header += '/' + myInst.config['IMP'+chan]

            if not myInst.config_section.has_option(myInst.config.name, 'LEV'+chan):
                return f'There is no LEV{chan} option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"SENS:EVEN{chan}:LEV:AUTO OFF")
                myInst.inst.write(f"SENS:EVEN{chan}:LEV {myInst.config['LEV'+chan]}")
                str_header += '/' + myInst.config['LEV'+chan]

            if not myInst.config_section.has_option(myInst.config.name, 'SLO'+chan):
                return f'There is no SLO{chan} option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"SENS:EVEN{chan}:SLOP {myInst.config['SLO'+chan]}")
                str_header += '/' + myInst.config['SLO'+chan]
            str_header += '\n'

    elif myInst.instModel == 'SR620':
        myInst.inst.write('*RST')
        myInst.inst.write('*CLS')
        myInst.inst.write('TENA 4')
        myInst.inst.write('*SRE 8')

        if not myInst.config_section.has_option(myInst.config.name, 'CONF'):
            return 'There is no CONF option in section ' + myInst.config.name
        else:
            if myInst.config['CONF'] == 'FREQ':
                myInst.inst.write('MODE 3')
            elif myInst.config['CONF'] == 'TINT':
                myInst.inst.write('MODE 0')
        
        if not myInst.config_section.has_option(myInst.config.name, 'CHAN'):
            return 'There is no CHAN option in section ' + myInst.config.name
        else:
            if myInst.config['CHAN'] == '1':
                myInst.inst.write('SRCE 0')
            elif myInst.config['CHAN'] == '2':
                myInst.inst.write('SRCE 1')
            else:
                myInst.inst.write('SRCE 0')
        chans = [myInst.config['CHAN'][0], myInst.config['CHAN'][-1]]
        str_header += 'Configure/Ch = ' + myInst.config['CONF'] + '/' + myInst.config['CHAN'] + '\n'

        #myInst.inst.write('GATE 1')
        myInst.inst.write('ARMM 5')
        myInst.inst.write('SIZE 1')
        myInst.inst.write('AUTM 1')
            
        for chan in chans:
            str_header += 'CH' + chan + '  Setting = '
            if not myInst.config_section.has_option(myInst.config.name, 'COUP'+chan):
                return f'There is no COUP{chan} option in section ' + myInst.config.name
            else:
                if myInst.config['COUP'+chan] == 'DC': myInst.inst.write(f'TCPL {chan}, 0')
                elif myInst.config['COUP'+chan] == 'AC': myInst.inst.write(f'TCPL {chan}, 1')
                else: raise Exception
                str_header += myInst.config['COUP'+chan]

            if not myInst.config_section.has_option(myInst.config.name, 'IMP'+chan):
                return f'There is no IMP{chan} option in section ' + myInst.config.name
            else:
                if myInst.config['IMP'+chan] == 'HIGH' or myInst.config['IMP'+chan] == '1M':
                    myInst.config['IMP'+chan] = '1E6'
                if myInst.config['IMP'+chan] == '50': myInst.inst.write(f'TERM {chan}, 0')
                elif myInst.config['IMP'+chan] == '1E6': myInst.inst.write(f'TERM {chan}, 1')
                else: raise Exception
                str_header += '/' + myInst.config['IMP'+chan]
                
            if not myInst.config_section.has_option(myInst.config.name, 'LEV'+chan):
                return f'There is no LEV{chan} option in section ' + myInst.config.name
            else:
                myInst.inst.write(f"LEVL {chan}, {myInst.config['LEV'+chan]}")
                str_header += '/' + myInst.config['LEV'+chan]
                
            if not myInst.config_section.has_option(myInst.config.name, 'SLO'+chan):
                return f'There is no SLO{chan} option in section ' + myInst.config.name
            else:
                if myInst.config['SLO'+chan] == 'POS': myInst.inst.write(f'TSLP {chan}, 0')
                elif myInst.config['SLO'+chan] == 'NEG': myInst.inst.write(f'TSLP {chan}, 1')
                else: raise Exception
                str_header += '/' + myInst.config['SLO'+chan]
            str_header += '\n'

    else:
        return 'This instrument model is not supported. (' + myInst.config.name + ')'
    
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
            f.write(str_header)
            f.write('\n')
            f.write('MJD   HH:mm:ss.ss MEASUREMENT\n')
    return 'Done'