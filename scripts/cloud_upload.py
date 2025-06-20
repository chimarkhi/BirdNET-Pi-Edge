import argparse
import os
import sqlite3
import textwrap
import datetime
import time

import json
import numpy as np
import pandas as pd
import requests
from utils.helpers import DB_PATH, FONT_DIR, get_settings, get_font


## Fetch data as array of jsons from DB
def get_data(start_time=None, limit=100):
    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    if start_time is None:
        start_time = datetime.datetime.now() - datetime.timedelta(days=1)
        start_time = start_time.timestamp()
    query = f"SELECT *, CAST(strftime('%s', datetime(Date, Time)) as integer) as evt_timestamp from detections WHERE datetime(Date,Time) > datetime({start_time}, 'unixepoch') limit {limit};"
    df = pd.read_sql_query(query, conn)
    df['device_id'] = os.uname().nodename
    # Drop date and time columns
    max_fetched_time = df['evt_timestamp'].max() ##TODO: this works because each file has a 15s different epoch, checkpoint should be made robust
    df = df.drop(columns = ['Date', 'Time'])

    
    # TODO: return an array of jsons so that data can be batch processed
    data_packet = df.to_json(orient='records')
    data_packet = json.loads(data_packet)
    
    data_packet = [{k.lower(): v for k,v in dict.items()} for dict in data_packet]
    #data_packet = df.to_json()
    return data_packet, max_fetched_time

# TODO: make a data class and the api calls a method of those classes
def upload_audio(data_record, conf):
    headers = {'device_id': data_record['device_id']}
    headers.update({'file_name': data_record['file_name']})
    headers.update({'Content-Type': 'audio/basic'})
    audio_file = os.path.join(conf['CLOUD_UPLOAD_DIR'], data_record['file_name'])
    try:
        with open(audio_file, 'rb') as f:
            data = f.read()
        audio_post_url = conf['AUDIO_POST_URL']
        response = requests.post(audio_post_url, headers=headers, data=data)
        if response.status_code == requests.codes.ok:
            print(f'{audio_file} succesfully uploaded, deleting file from disk')
            os.remove(audio_file)
            return response.status_code
    except FileNotFoundError:
        print(f"File {audio_file} not found, skipping upload")
        return requests.codes.ok

## Post data and save checkpoint
def main(daemon, sleep_m):
    conf = get_settings()
    default_last_run = datetime.datetime.now() - datetime.timedelta(days=int(conf['INFERENCE_UPLOAD_DEFAULT_RESETDAYS']))
    default_last_run = default_last_run.timestamp()
    last_run = default_last_run
    checkpoint_file = os.path.join(conf['CLOUD_UPLOAD_DIR'], 'last_upload_checkpoint.json')
    try:
        with open(checkpoint_file, 'r') as file:
            checkpoint = json.load(file)
            last_run = int(checkpoint['epoch'])
            if last_run > datetime.datetime.now().timestamp():
                print(f"file epoch is greater than right now {last_run}, {datetime.datetime.now().timestamp()}")
                last_run = default_last_run
    except FileNotFoundError:
        print("No checkpoint found")
    except json.decoder.JSONDecodeError:
        print("Corrupted checkpoint; reseting the file")
        with open(checkpoint_file, 'w') as file:
            json.dump({"epoch": last_run}, file)

    while True:
        time.sleep(2)
        data_packet, max_epoch = get_data(last_run)
        if len(data_packet) == 0:
            print("No new inferred data")
        else:
            print(f"{len(data_packet)} new records found since last checkpoint")
            for i in range(len(data_packet)):                
                response = requests.post(conf['SPECIESID_POST_URL'], json=data_packet[i])
                if response.status_code == requests.codes.ok:
                    rc = upload_audio(data_packet[i], conf)
                    if rc == requests.codes.ok:
                        with open(checkpoint_file, 'w') as file:
                            json.dump({"epoch": str(data_packet[i]['evt_timestamp'])}, file)
                        print(f"Data uploaded; checkpoint updated to {data_packet[i]['evt_timestamp']}")
                    else:
                        print(f"Raw Data upload failed with code {response.status_code} and error: {response.json}")
                else:
                    print(f"Species ID POST request failed with code {response.status_code} and error: {response.json}")
        # TODO: fix daemon mode
        #if daemon: 
        #    sleep(60*sleep_m)
        #else:
        #    sleep(60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--daemon', action='store_true')
    parser.add_argument('--sleep', default=2, type=int, help='Time between runs (minutes)')
    args = parser.parse_args()
    main(args.daemon, args.sleep)
