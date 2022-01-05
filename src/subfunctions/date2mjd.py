def date2mjd(year, month, day):
    
    ## Check inputs
    if isinstance(year, str) and isinstance(month, str) and isinstance(day, str):
        flag_strOut = True
        year = int(year)
        month = int(month)
        day = int(day)
    elif isinstance(year, int) and isinstance(month, int) and isinstance(day, int):
        flag_strOut = False
    else:
        return None
        
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    
    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = int(yearp / 100.)
        B = 2 - A + int(A / 4.)
        
    if yearp < 0:
        C = int((365.25 * yearp) - 0.75)
    else:
        C = int(365.25 * yearp)
    D = int(30.6001 * (monthp + 1))
    
    jd = B + C + D + day + 1720994.5
    
    if flag_strOut:
        mjd = str(int(jd - 2400000.5))
    else:
        mjd = int(jd - 2400000.5)

    return mjd