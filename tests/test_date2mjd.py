from datetime import date, timedelta
from src.subfunctions.date2mjd import date2mjd
import unittest

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

class BasicTestSuite(unittest.TestCase):
    
    def test_2020(self):
        YEAR = 2020
        mjd = 58849
        for i in daterange(date(YEAR, 1, 1), date(YEAR, 12, 31)):
            self.assertEqual(date2mjd(i.strftime("%Y"), i.strftime("%m"), i.strftime("%d")), str(mjd)) # Insert inputs with string type
            self.assertEqual(date2mjd(int(i.strftime("%Y")), int(i.strftime("%m")), int(i.strftime("%d"))), mjd) # Insert inputs with integer type
            mjd += 1
            
    def test_2021(self):
        YEAR = 2021
        mjd = 59215
        for i in daterange(date(YEAR, 1, 1), date(YEAR, 12, 31)):
            self.assertEqual(date2mjd(i.strftime("%Y"), i.strftime("%m"), i.strftime("%d")), str(mjd)) # Insert inputs with string type
            self.assertEqual(date2mjd(int(i.strftime("%Y")), int(i.strftime("%m")), int(i.strftime("%d"))), mjd) # Insert inputs with integer type
            mjd += 1
            
    def test_2022(self):
        YEAR = 2022
        mjd = 59580
        for i in daterange(date(YEAR, 1, 1), date(YEAR, 12, 31)):
            self.assertEqual(date2mjd(i.strftime("%Y"), i.strftime("%m"), i.strftime("%d")), str(mjd)) # Insert inputs with string type
            self.assertEqual(date2mjd(int(i.strftime("%Y")), int(i.strftime("%m")), int(i.strftime("%d"))), mjd) # Insert inputs with integer type
            mjd += 1
            
    def test_2023(self):
        YEAR = 2023
        mjd = 59945
        for i in daterange(date(YEAR, 1, 1), date(YEAR, 12, 31)):
            self.assertEqual(date2mjd(i.strftime("%Y"), i.strftime("%m"), i.strftime("%d")), str(mjd)) # Insert inputs with string type
            self.assertEqual(date2mjd(int(i.strftime("%Y")), int(i.strftime("%m")), int(i.strftime("%d"))), mjd) # Insert inputs with integer type
            mjd += 1

if __name__ == '__main__':
    unittest.main()