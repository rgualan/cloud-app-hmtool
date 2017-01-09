import csv
import os
from server.settings import *
from google.appengine.ext import ndb

csv_test_data = PROJECT_DIR+'/../data/Station1_min5_2000.csv'

def get_test_data():
    """ Reads and returns the data from a CSV file"""
    with open(csv_test_data, 'rb') as csvfile:
        cursor = csv.reader(csvfile, delimiter=',', quotechar='"')
        i = 0
        data = []
        for row in cursor:
            if row[0][0] == '#':
                pass
            else:
                data.append(row)
                i = i + 1            
                
    return data