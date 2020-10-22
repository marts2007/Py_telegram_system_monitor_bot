import psutil
from logger import log
from config import config
from datetime import datetime, date, time

userlist = {}
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
    result = True
    for drive in config.drives:
       drv = psutil.disk_usage(drive['path'])
       if drv.percent > drive['maxusage']:
           drive['exceeded'] = 1
           result = False
           config.store_config()
       else:
           drive['exceeded'] = 0
           drive['alerted']= 0
           config.store_config()

    return result

def get_idle_pids():
    piddata = {}
    pidlist = []
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            process = {}
            process['name'] = proc.name()
            process['id'] = proc.pid
            userName = proc.username()
            process['username'] = userName
            process['memory_percent'] = proc.memory_percent(memtype="rss")
            process['memory_info'] = ((proc.memory_info()).rss / 1e9)
            process['status'] = proc.status()
            process['foundtime'] = datetime.now().timestamp()
            if (process['status'] != 'running' and process['memory_info'] > 2):
              pidlist.append(process['id'])
              if config.sleeping_pids.get(str(process['id'])) != None:
                process['foundtime']=config.sleeping_pids[str(process['id'])]['foundtime']
              piddata[str(process['id'])]=process

        except (
        psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    #proctop.sort(key=lambda ar: -ar['memory_info'])
    config.change('sleeping_pids',piddata)
    config.store_config()
    return [piddata,pidlist]

def get_top_ram_users():
    psutil.process_iter(attrs=None, ad_value=None)
    usertop = []
    userlist = {}
    for proc in psutil.process_iter():
        try:
            process = {}
            process['name'] = proc.name()
            process['id'] = proc.pid
            userName = proc.username()
            process['memory_percent'] = proc.memory_percent(memtype="uss")
            process['status'] = proc.status()
            cpu = proc.status()
            if userName in userlist:
                userlist[userName]['memory'] += process['memory_percent']
                userlist[userName]['processes'].append(process)
                userlist[userName]['processes'].sort(key=lambda ar: -ar['memory_percent'])
            else:
                userlist[userName] = {   'memory' : process['memory_percent'],
                                        'processes' : [process]
                                      }
                usertop.append(userName)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    usertop.sort(key=lambda ar: -userlist[ar]['memory'] )
    return usertop,userlist

checkDrives()