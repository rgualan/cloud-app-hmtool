import csv
import os
from server.settings import *
from google.appengine.ext import ndb

#PROJECT_DIR = os.path.dirname(__file__)

csv_test_data = PROJECT_DIR+'/../data/Station1_min5_2000.csv'

def get_test_data_0():
    return testdata

def get_test_data():
    with open(csv_test_data, 'rb') as csvfile:
        cursor = csv.reader(csvfile, delimiter=',', quotechar='"')
        #limit = 100
        i = 0
        data = []
        for row in cursor:
            #print row
            if row[0][0] == '#':
                pass
            else:
                data.append(row)
                i = i + 1            
                
            #if limit and i == limit:
            #    break
    return data