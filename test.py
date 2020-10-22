import system_monitor as sm
import time
import os
from config import config
longlist = set()
prevlist = set()
procstat = {}
from datetime import datetime, date, time


piddata,pidlist=sm.get_idle_pids()

for id, process in piddata.items():
     datefrom=datetime.fromtimestamp(process['foundtime'])
     seconds = (datetime.now() - datefrom).seconds
     runing_time = "{}h {}m".format(int(seconds /  3600),int((seconds/60) % 60))
     print( process['username'], ' ',
                process['id'], ':', process['name'],
                ':', process['status'], ':', round(process['memory_info'], 2),
                'GB', datefrom,':', runing_time)

quit()

while True:

     proctop, pidlist = sm.get_idle_pids()
     longlist=set(prevlist).intersection(set(pidlist))
     prevlist=pidlist
     os.system('clear')
     for process in proctop:
          if process['id'] in longlist:
               if process['id'] in procstat:
                    count= procstat[process['id']]+1
               else:
                    count=1
               procstat[process['id']] = count
               print(procstat[process['id']],' ',process['username'], ' ', process['id'], ':', process['name'],
                     ':', process['status'], ':', round(process['memory_info'],2), 'GB')

     time.sleep(60*60*2)
