def apply_presets(inst):
    if inst.instModel == '53230A':
            inst.inst.write('ABOR') # Abort (=quit) measuring if any exists.
            inst.inst.write('*RST') # Reset
            inst.inst.write('*CLS') # Clear the Status Byte Register
            inst.inst.write('DATA:POIN:EVEN:THR 1') #' + inst.config['READCNT']) # Measurement count threshold is set to 1.
            inst.inst.write('STAT:OPER:ENAB 4096') # Relation between the event and Standard Operation Register. (If measurement count exceed the threshold, SOR is turned on.)
            inst.inst.write('*SRE 128') # Relation between the Status Byte Register and RQS (6th bit of SBR).
            inst.inst.write('ROSC:SOUR:AUTO ON') # Reference oscillator is automatically selected.
            #inst.inst.write('SYST:TIM 10')

            if inst.config['CONF'] == 'FREQ':
                inst.inst.write(f"CONF:{inst.config['CONF']} (@{inst.config['CHAN']}")
                inst.inst.write('TRIG:COUN 1')
                inst.inst.write('FREQ:MODE CONT')
                inst.inst.write('SENS:FREQ:GATE:SOUR TIME')
                inst.inst.write('SENS:FREQ:GATE:TIME 1')
                
            elif inst.config['CONF'] == 'TINT':
                inst.inst.write(f"CONF:{inst.config['CONF']} (@{inst.config['CHAN'][0]}),(@{inst.config['CHAN'][-1]})")
                inst.inst.write('TRIG:COUN 1E6')
                
            else:
                inst.inst.write(f"CONF:{inst.config['CONF']}")

            inst.inst.write('INP1:COUP ' + inst.config['COUP1'])
            inst.inst.write('INP2:COUP ' + inst.config['COUP2'])
            if inst.config['IMP1'] == 'HIGH' or inst.config['IMP1'] == '1M':
                inst.config['IMP1'] = '1E6'
            inst.inst.write('INP1:IMP ' + inst.config['IMP1'])
            if inst.config['IMP2'] == 'HIGH' or inst.config['IMP2'] == '1M':
                inst.config['IMP2'] = '1E6'
            inst.inst.write('INP2:IMP ' + inst.config['IMP2'])
            inst.inst.write('INP1:LEV ' + inst.config['LEV1'])
            inst.inst.write('INP2:LEV ' + inst.config['LEV2'])
            inst.inst.write('INP1:SLOP ' + inst.config['SLO1'])
            inst.inst.write('INP2:SLOP ' + inst.config['SLO2'])
            #inst.inst.write('TRIG:SOUR IMM')
            inst.inst.write('SAMP:COUN 1E6') # Set as maximum
            
            
            
    elif inst.instModel == '53132A' or inst.instModel == '53131A':
        inst.inst.write('ABOR') # Abort (=quit) measuring if any exists.
        inst.inst.write('*RST') # Reset
        inst.inst.write('*CLS') # Clear the Status Byte Register
        inst.inst.write(':STAT:PRESet')
        inst.inst.write(':STAT:OPER:PTR 0; NTR 16') # Rule for detecting a negative transition (?)
        inst.inst.write(':STAT:OPER:ENAB 16') # Masking Operation Status Register to represent 4th bit(Measuring) only.
        inst.inst.write('*SRE 128')

        inst.inst.write('ROSC:SOUR:AUTO ON') # Reference oscillator is automatically selected.
        
        inst.inst.write('CONF:' + inst.config['CONF'])
        inst.inst.write('INP1:COUP ' + inst.config['COUP1'])
        inst.inst.write('INP2:COUP ' + inst.config['COUP2'])
        if inst.config['IMP1'] == 'HIGH' or inst.config['IMP1'] == '1M': inst.config['IMP1'] = '1E6'
        inst.inst.write('INP1:IMP '+inst.config['IMP1'])
        if inst.config['IMP2'] == 'HIGH' or inst.config['IMP2'] == '1M': inst.config['IMP2'] = '1E6'
        inst.inst.write('INP2:IMP '+inst.config['IMP2'])
        inst.inst.write('SENS:EVEN1:LEV:AUTO OFF')
        inst.inst.write('SENS:EVEN2:LEV:AUTO OFF')
        inst.inst.write('SENS:EVEN1:LEV ' + inst.config['LEV1'])
        inst.inst.write('SENS:EVEN2:LEV ' + inst.config['LEV2'])
        inst.inst.write('SENS:EVEN1:SLOP ' + inst.config['SLO1'])
        inst.inst.write('SENS:EVEN2:SLOP ' + inst.config['SLO2'])

    elif inst.instModel == 'SR620':
        inst.inst.write('*RST')
        inst.inst.write('*CLS')
        inst.inst.write('TENA 4')
        inst.inst.write('SIZE 1')
        inst.inst.write('SRCE 0')
        inst.inst.write('*SRE 8')

        if inst.config['CONF'] == 'TINT':
            inst.inst.write('MODE 0')
        if inst.config['COUP1'] == 'DC': inst.inst.write('TCPL 1, 0')
        elif inst.config['COUP1'] == 'AC': inst.inst.write('TCPL 1, 1')
        else: raise Exception
        if inst.config['COUP2'] == 'DC': inst.inst.write('TCPL 2, 0')
        elif inst.config['COUP2'] == 'AC': inst.inst.write('TCPL 2, 1')
        else: raise Exception
        if inst.config['IMP1'] == '50': inst.inst.write('TERM 1, 0')
        elif inst.config['IMP1'] == '1E6' or inst.config['IMP1'] == 'HIGH' or inst.config['IMP1'] == '1M': inst.inst.write('TERM 1, 1')
        else: raise Exception
        if inst.config['IMP2'] == '50': inst.inst.write('TERM 2, 0')
        elif inst.config['IMP1'] == '1E6' or inst.config['IMP1'] == 'HIGH' or inst.config['IMP1'] == '1M': inst.inst.write('TERM 2, 1')
        else: raise Exception
        inst.inst.write('LEVL 1, ' + inst.config['LEV1'])
        inst.inst.write('LEVL 2, ' + inst.config['LEV2'])
        if inst.config['SLO1']=='POS': inst.inst.write('TSLP 1,0')
        elif inst.config['SLO1']=='NEG': inst.inst.write('TSLP 1, 1')
        else: raise Exception
        if inst.config['SLO2']=='POS': inst.inst.write('TSLP 2,0')
        elif inst.config['SLO2']=='NEG': inst.inst.write('TSLP 2, 1')
        else: raise Exception
    else:
        return None
    
    return True