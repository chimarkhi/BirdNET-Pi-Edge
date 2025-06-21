import argparse
import os
import sqlite3
import textwrap
import datetime
import time
import signal
import sys

import json
import numpy as np
import pandas as pd
import requests
from utils.helpers import DB_PATH, FONT_DIR, get_settings, get_font
import logging

log = logging.getLogger(__name__)

shutdown = False

def sig_handler(sig_num, curr_stack_frame):
    global shutdown
    log.info('Caught shutdown signal %d', sig_num)
    shutdown = True
    exit()

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
            log.info(f'{audio_file} succesfully uploaded, deleting file from disk')
            os.remove(audio_file)
            return response.status_code
    except FileNotFoundError:
        log.error(f"File {audio_file} not found, skipping upload")
        return requests.codes.ok

## Post data and save checkpoint
def main(daemon, sleep_m):
    conf = get_settings()
    default_last_run = datetime.datetime.now() - datetime.timedelta(days=int(conf['INFERENCE_UPLOAD_DEFAULT_RESETDAYS']))
    default_last_run = default_last_run.timestamp()
    last_run = default_last_run
    checkpoint_file = os.path.join(conf['CLOUD_UPLOAD_DIR'], 'last_upload_checkpoint.json')

    while True:
        try:
            with open(checkpoint_file, 'r') as file:
                checkpoint = json.load(file)
                last_run = int(checkpoint['epoch'])
                if last_run > datetime.datetime.now().timestamp():
                    log.warning(f"file epoch is greater than right now {last_run}, {datetime.datetime.now().timestamp()}")
                    last_run = default_last_run
        except FileNotFoundError:
            log.warning("No checkpoint found")
        except json.decoder.JSONDecodeError:
            log.warning("Corrupted checkpoint; reseting the file")
            with open(checkpoint_file, 'w') as file:
                json.dump({"epoch": last_run}, file)

        data_packet, max_epoch = get_data(last_run)
        if len(data_packet) == 0:
            log.warning("No new inferred data")
        else:
            log.info(f"{len(data_packet)} new records found since last checkpoint")
            for i in range(len(data_packet)):                
                response = requests.post(conf['SPECIESID_POST_URL'], json=data_packet[i])
                if response.status_code == requests.codes.ok:
                    rc = upload_audio(data_packet[i], conf)
                    if rc == requests.codes.ok:
                        with open(checkpoint_file, 'w') as file:
                            json.dump({"epoch": str(data_packet[i]['evt_timestamp'])}, file)
                        log.info(f"Data uploaded; checkpoint updated to {data_packet[i]['evt_timestamp']}")
                    else:
                        log.error(f"Raw Data upload failed with code {response.status_code} and error: {response.json}")
                else:
                    log.error(f"Species ID POST request failed with code {response.status_code} and error: {response.json}")
        if daemon:
            time.sleep(60 * sleep_m)
        else:
            break

def setup_logging():
    logger = logging.getLogger()
    formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    global log
    log = logging.getLogger('cloud_upload')

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument('--daemon', action='store_true')
    parser.add_argument('--sleep', default=2, type=int, help='Time between runs (minutes)')
    args = parser.parse_args()
    setup_logging()

    main(args.daemon, args.sleep)
