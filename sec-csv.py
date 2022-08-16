# Used to use split in map
from code import compile_command
from operator import methodcaller
from typing import Tuple

# Used to access content of URL
import requests

# json package
import json

# Used to get uniform random sample
from numpy import random as rd

# To pause execution
import time 

# csv package
import csv

# How large is the sample?
# Extracted with: num_lines = sum(1 for line in open('ticker.txt'))

total_companies = 12175
number_of_samples = 400

# Pick random sample uniform over [1,total_companies]
samples = rd.randint(0,total_companies,number_of_samples)

# Store list of companies as a list with elements of the form ['name','identifier']
lines_list_raw = map(str.strip, open('ticker.txt').readlines())
lines_list = list(map(methodcaller('split', '\t'), lines_list_raw))

# Generate list of identifies to read
id_samples = [ lines_list[i][1] for i in samples]

data_base = []
my_list = id_samples

for id in my_list:
    print('Checking ' + id.zfill(10))
    
    link_test = 'https://data.sec.gov/submissions/CIK{}.json'.format(id.zfill(10))
    # First link contains entityType key

    # Header to make request go through
    hdr = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}
    
    response_test = requests.get(link_test,headers=hdr)
    # Content is now of type byte
    byte_content_test = response_test.content
    # Content is now of type string
    string_content_test = byte_content_test.decode("utf-8")
    # Content is now a json 
    json_content_test = json.loads(string_content_test)

    if json_content_test['entityType'] == 'operating':
        # Only look at operating entities
        link = 'https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json'.format(id.zfill(10))
        response = requests.get(link,headers=hdr)
        byte_content = response.content
        string_content = byte_content.decode("utf-8")
        try:
            json_content = json.loads(string_content)

            if 'entityName' in json_content:
                # print('Getting information on ' + json_content['entityName'])
                if 'facts' in json_content:
                    if 'us-gaap' in json_content['facts']:
                        if 'CommonStockSharesOutstanding' in json_content['facts']['us-gaap']:
                            shares = json_content['facts']['us-gaap']['CommonStockSharesOutstanding']['units']['shares'][-1]['val']
                            # print('CommonStockSharesOutstanding is ' + str(shares))
                            data_base.append((shares,json_content['entityName']))
                        elif 'PreferredStockSharesOutstanding' in json_content['facts']['us-gaap']:
                            shares = json_content['facts']['us-gaap']['PreferredStockSharesOutstanding']['units']['shares'][-1]['val']
                            # print('PreferredStockSharesOutstanding is ' + str(shares))
                            data_base.append((shares,json_content['entityName']))
        except:
            print('No viable .json file available at ' + link)

data_base = sorted(data_base)

with open("out_data.csv", "wt") as fp:
    writer = csv.writer(fp, delimiter=",")
    # writer.writerow(["your", "header", "foo"])  # write header
    writer.writerows(data_base)

# Testing the try and except commands... 
# hdr = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}
# link = 'https://data.sec.gov/api/xbrl/companyfacts/CIK0001622148.json'
# response = requests.get(link,headers=hdr)
# byte_content = response.content
# string_content = byte_content.decode("utf-8")
# try:
#     json_content = json.loads(string_content)
# except:
#     print('No .json file available.')


 
