#!/bin/env python3
import logging
from sys import platform, getfilesystemencoding
from os import uname
from collections import namedtuple
from jproperties import Properties
from splunk_hec_handler import SplunkHecHandler

# setup logger utility for this script
logging.basicConfig(filename='transmute.log', filemode='w',format='%(asctime)s - PID:%(process)d - %(name)s - %(message)s', level=logging.INFO)

# global vars
SYSTEM_OS = platform
ENCODING = getfilesystemencoding()

# create logger specifically for splunk data
splunk_logger = logging.getLogger('splunk_logger') 
splunk_logger.setLevel(logging.DEBUG)
# create and add log stream handler to it
stream_handler = logging.StreamHandler()
stream_handler.level = logging.DEBUG
splunk_logger.addHandler(stream_handler)

# splunk token
token = "EA33046C-6FEC-4DC0-AC66-4326E58B54C3"

# Create Handler to push data to Splunk HTTP Event Collector
splunk_handler = SplunkHecHandler('sample.splunk.domain.com',
                                 token, index="hec",
                                 port=8080, proto='http', ssl_verify=False,
                                 source="evtx2json", sourcetype='xxxxxxxx_json')
splunk_logger.addHandler(splunk_handler)

# add additional fields and corresponding values to splunk
dict_obj = {'fields': {'color': 'yellow', 'api_endpoint': '/results', 'host': 'app01', 'index':'hec'},
            'user': 'foobar', 'app': 'my demo', 'severity': 'low', 'error codes': [1, 23, 34, 456]}
# send sample data to splunk_logger
splunk_logger.info(dict_obj)

# specify splunk ingestion parameters adhoc like so:
log_summary_evt = {'fields': {'index': 'adhoc', 'sourcetype': '_json', 'source': 'adv_example'}, 'exit code': 0, 'events logged': 100}
splunk_logger.debug(log_summary_evt)

# load java properties
p = Properties()
jpfile = '/home/kafka/apps/kafka/config/log4j.properties'
with open(jpfile, 'rb') as f:
    p.load(f, ENCODING)
# add to dictionary
log4j_json = dict()
log4j_json['source_file'] = jpfile
log4j_json.update(p)
# send to splunk
splunk_logger.info({'fields': p})

def os_enrich(prune_output=True):
    """
    returns dict of useful OS information
    """
    osvars = uname()
    os_data = { 'system_os': SYSTEM_OS,
                'fs_enconding': ENCODING,
                'sysname': osvars.sysname,
                'nodename': osvars.nodename,
                'machine': osvars.machine,
                'os_version': osvars.version,
                'os_release': osvars.release
    }
    return os_data

# send more data
splunk_logger.info({'fields': os_enrich()})

# you get the idea
splunk_logger.info({'fields': os.environ})
