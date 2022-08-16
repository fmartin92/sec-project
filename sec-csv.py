import csv
import json
from numpy import random as rd
import logging
import requests
from typing import Tuple

logging.basicConfig(filename='logging.log', encoding='utf-8', level=logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
# Requests generates log messages. Increase level to ignore them.
# For some reason the correct name here is urllib3 although we are using the requests package.

def main():

    # How large is the sample?
    TOTAL_COMPANIES = sum(1 for line in open('ticker.txt'))
    NUMBER_OF_SAMPLES = 20

    # Pick random sample uniform over [0, TOTAL_COMPANIES - 1], since we are picking indices of lines.
    samples = rd.randint(0, TOTAL_COMPANIES -1, NUMBER_OF_SAMPLES)

    # Store list of companies as a list with elements of the form ['name', 'identifier'].
    lines_list_raw = map(str.strip, open('ticker.txt').readlines())
    lines_list = list(map(lambda line: line.split('\t'), lines_list_raw))

    # Generate list of identifiers to read.
    id_samples = [lines_list[i][1] for i in samples]
    
    # A list of tuples (shares, company id).
    # Should ideally be (company id, shares), must re-do, and fix sorting later.
    database : list[Tuple[int, str]] = []

    # Header to make request go through.
    HDR = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}

    for id in id_samples:
        logging.debug('Checking ' + f'{int(id):010d}')
        link = f'https://data.sec.gov/submissions/CIK{int(id):010d}.json'
        # First link contains entityType key. 
        json_content = json.loads(requests.get(link, headers=HDR).content.decode('utf-8'))

        if json_content['entityType'] == 'operating':
            # Only look at operating entities.
            link = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(id):010d}.json'
            response = requests.get(link, headers=HDR)
            
            try:
                json_content = json.loads(response.content.decode('utf-8'))

                if 'entityName' in json_content and 'facts' in json_content and 'us-gaap' in json_content['facts']:
                    shares = 0
                    gaap = json_content['facts']['us-gaap']

                    if 'CommonStockSharesOutstanding' in gaap:
                        shares = gaap['CommonStockSharesOutstanding']['units']['shares'][-1]['val']

                    elif 'PreferredStockSharesOutstanding' in gaap:
                        shares = gaap['PreferredStockSharesOutstanding']['units']['shares'][-1]['val']
                        
                    database.append((shares, json_content['entityName']))
                else:
                    logging.debug('Found no information on outstanding shares.')
                    continue
            except:
                logging.debug('No viable .json file available at ' + link)
        else:
            logging.debug('Entity is not operating')

    database = sorted(database)

    with open('out_data.csv', 'wt') as fp:
        writer = csv.writer(fp, delimiter=',')
        writer.writerows(database)

if __name__=='__main__':
    main()



 
