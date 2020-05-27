import psutil
from logger import log
from config import config


conf = {
        'apikey': '',
        'user_list': [],
        'drives': [  # drives to monitor
            {
                'path': '/',
                'minspace': 95,
                'report_file': '',
            },

        ],
        'proxies': {
            "https": "http://192.168.0.3:8118"
            # remove this line if you do not need proxy
        },
        'lastupdate_id': 0
    }

def checkSystem():
    return checkDrives()


def checkDrives():
    #print(conf['drives'])
    result = True
    for drive in config.drives:
       drv = psutil.disk_usage(drive['path'])
       if drv.percent > drive['maxusage']:
           drive['exceeded'] = 1
           result = False
       else:
           drive['exceeded'] = 0
           drive['alerted']= 0
    return result

checkDrives()