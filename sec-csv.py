# Used to use split in map
from code import compile_command

from typing import Tuple

# Used to access content of URL
import requests

import json

# Used to get uniform random sample
from numpy import random as rd

import csv

import logging

logging.basicConfig(filename='logging.log', encoding='utf-8', level=logging.DEBUG)

# Requests generates log messages. Increase level to ignore them.
# For some reason the correct name here is urllib3 
# although we are using the requests package.
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# How large is the sample?
TOTAL_COMPANIES = sum(1 for line in open('ticker.txt'))
NUMBER_OF_SAMPLES = 400

# Pick random sample uniform over [0, TOTAL_COMPANIES - 1], since we are picking indices of lines
samples = rd.randint(0, TOTAL_COMPANIES -1, NUMBER_OF_SAMPLES)

# Store list of companies as a list with elements of the form ['name','identifier']
lines_list_raw = map(str.strip, open('ticker.txt').readlines())
lines_list = list(map(lambda line: line.split('\t'), lines_list_raw))

# Generate list of identifies to read
id_samples = [ lines_list[i][1] for i in samples]

data_base = []

for id in id_samples:
    logging.debug('Checking ' + id.zfill(10))
    
    link_test = 'https://data.sec.gov/submissions/CIK{}.json'.format(id.zfill(10))
    # First link contains entityType key

    # Header to make request go through
    hdr = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}
    
    response_test = requests.get(link_test, headers=hdr)
    json_content_test = json.loads(response_test.content.decode("utf-8"))

    if json_content_test['entityType'] == 'operating':
        # Only look at operating entities
        
        link = 'https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json'.format(id.zfill(10))
        response = requests.get(link, headers=hdr)
        
        try:
            json_content = json.loads(response.content.decode("utf-8"))

            if 'entityName' in json_content and 'facts' in json_content and 'us-gaap' in json_content['facts']:
                shares = int()

                if 'CommonStockSharesOutstanding' in json_content['facts']['us-gaap']:
                    shares = json_content['facts']['us-gaap']['CommonStockSharesOutstanding']['units']['shares'][-1]['val']

                elif 'PreferredStockSharesOutstanding' in json_content['facts']['us-gaap']:
                    shares = json_content['facts']['us-gaap']['PreferredStockSharesOutstanding']['units']['shares'][-1]['val']
                    
                data_base.append((shares,json_content['entityName']))
        except:
            logging.debug('No viable .json file available at ' + link)

data_base = sorted(data_base)

with open("out_data.csv", "wt") as fp:
    writer = csv.writer(fp, delimiter=",")
    # writer.writerow(["your", "header", "foo"])  # write header
    writer.writerows(data_base)



 
