import psutil
from logger import log
from config import config

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
    #print(conf['drives'])
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



def get_top_ram_users():
    # Use a breakpoint in the code line below to debug your script.
    psutil.process_iter(attrs=None, ad_value=None)
    usertop = []
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            process = {}

            process['name'] = proc.name()
            process['id'] = proc.pid
            userName = proc.username()
            process['memory_percent'] = proc.memory_percent()
            process['status'] = proc.status()
            cpu = proc.status()
            if userName in userlist:
                userlist[userName]['memory'] += process['memory_percent']
                #list = userlist[userName]['processes']
                userlist[userName]['processes'].append(process)
                userlist[userName]['processes'].sort(key=lambda ar: -ar['memory_percent'])
            else:
                userlist[userName] = {   'memory' : process['memory_percent'],
                                        'processes' : [process]
                                      }
                usertop.append(userName)
            #print(processName , ' ::: ', processID,' ::: ', userName, ' ::: ', memory)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    #usertop = list(userlist.items())
    usertop.sort(key=lambda ar: -userlist[ar]['memory'] )
    return usertop,userlist


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#    usertop=get_process_list()
#    for user in usertop:
#        memory_usage=round(userlist[user]['memory'],2)
#        if memory_usage > 1:
#            print(user,' : ',memory_usage,'%')


checkDrives()