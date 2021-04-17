# This script was created in 2021 to attempt to book an appointment on the RiteAid site.
# This doesn't do web scraping, instead it calls the json services that are used on the website.
# This was discussed on an episode of Data Science Imposters.
import json
import os
import requests
import time

# The script failed on these zip codes so let's ignore them all together
IGNORE_ZIPS = {'08651', '08351', '08726', '08276', '08851', '08126', '07651', '08451', '07551', '07226', '07151', '07301', '08951', '08426', '08576', '07376', '08151', '07951', '07526', '08301', '07251', '07351'}

STORE_ZIP = dict()

CHECKED_STORES = set()

def get_store_ids(zip_code):
    url = 'https://www.riteaid.com/services/ext/v2/stores/getStores?address={}&attrFilter=PREF-112&radius=25'.format(zip_code)
    #print('trying url: {}'.format(url)) 
    response = requests.get(url)
    data = json.loads(response.content)
    stores = [] 
    try: 
        for store in data['Data']['stores']:
            if store['state'] == 'NJ': 
                stores.append(store['storeNumber'])
                STORE_ZIP[store['storeNumber']] = zip_code 
    except:
        IGNORE_ZIPS.add(zip_code) 
        return None

    return stores

def get_store_availability(store_number):
    url = 'https://www.riteaid.com/services/ext/v2/vaccine/checkSlots?storeNumber={}'.format(store_number)
    response = requests.get(url)
    data = json.loads(response.content)
    for idx, slot_available in data['Data']['slots'].items():
        if slot_available:
            print('\n\n========Available for ZIP store_number {}, {}==========\n\n'.format(STORE_ZIP[store_number], store_number, idx))
            os.system("beep -f 555 -l 460")

def main():
    for zip in range(7001,8989,50):
        if zip in IGNORE_ZIPS:
            continue

        stores = get_store_ids(str(zip).zfill(5))
        if not stores:
            continue
        #stores = [1977, ]
        for store in stores:
            if store in CHECKED_STORES:
                continue
            else: 
                get_store_availability(store)
                CHECKED_STORES.add(store)
        #print('sleeping 5 seconds')
        time.sleep(5)

    print('Ignore these zips:')
    print(IGNORE_ZIPS)

while True:
    main()
    print('sleeping 2  minutes') 
    time.sleep(2*60)
