import system_monitor as sm
import time
import os
longlist = set()
prevlist = set()
procstat = {}
while True:

     proctop, pidlist = sm.get_sleeping_pids()
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
