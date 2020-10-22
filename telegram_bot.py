import json
from logger import log
import http_fetcher as ht
import system_monitor as sm
from config import config
import time
import socket
import os.path
import psutil
from datetime import datetime, date

class Telegram:
    def do_tel_query(self, action: str = 'getMe', params: dict = {}):
        print(action)
        response = (ht.get_url('https://api.telegram.org/bot'+config.apikey+'/'+action, params))
        return response
    def send_message_all(self,text):
        for user in  config.subscribers:
            self.send_message(user,text)

    def send_message(self, chat_id, text):
        response = self.do_tel_query('sendMessage', {'chat_id': chat_id,'text': text})

    def __init__(self) -> None:
        response = self.do_tel_query('getMe')
        if type(response) == dict:
            if 'ok' in response:
                if response['ok']:
                    self.status = True
                    log('Connection succeeded')
                    self.mainloop()
        self.status = False

    def mainloop(self):
        while 1:
            if not sm.checkSystem():
                for drive in config.drives:
                    if drive['exceeded']:
                        message = "{} \r\n\r\nLow free space on {}\r\n\r\n".format(socket.gethostname(),drive['path'])
                        if os.path.isfile(drive['report_file']):
                            message += open(drive['report_file'], 'r').read()
                        if not drive['alerted']:
                            drive['alerted'] = 1
                            config.store_config()
                            self.send_message_all(message)
                pass
            self.get_updates()
            time.sleep(5)

    def get_updates(self):
        response = self.do_tel_query('getUpdates', {'offset': int(config.lastupdate_id)+1})
        if type(response) == dict:
            if 'ok' in response:
                if 'result' in response:
                    if len(response['result']) > 0:
                        for resp in response['result']:
                            config.change('lastupdate_id', resp['update_id'])
                            print(resp)
                            self.parse_message(resp['message'])
        return response


    def parse_message(self,msg: dict = {}):
        if msg['text'].find('/subscribe') > -1:
            config.change('subscribers', list(set(config.subscribers if config.subscribers else {}) | {msg['chat']['id'],}))
            self.send_message(msg['chat']['id'], 'You have been subscribed')
        if msg['text'].find('/unsubscribe') > -1:
            config.change('subscribers', list(set(config.subscribers if config.subscribers else {}) - {msg['chat']['id']}))
            self.send_message(msg['chat']['id'], 'You have been unsubscribed')
        if msg['text'].find('/info') > -1:
            message = ''
            for drive in config.drives:
                drv = psutil.disk_usage(drive['path'])
                message += "Filesystem {} \r\nTotal: {} GiB\r\n".format(drive['path'], round(drv.total / (2**30),1))
                message += "Used: {} GiB\r\n".format(round(drv.used / (2**30),1))
                message += "Free: {} GiB\r\n\r\n".format(round(drv.free / (2**30),1))
                if os.path.isfile(drive['report_file']):
                    message += open(drive['report_file'], 'r').read()
                    message += "\r\n\r\n"

            usertop, userlist =  sm.get_top_ram_users()
            message += "Memory Usage:\r\n"
            for user in usertop:
                memory_usage = round(userlist[user]['memory'], 2)
                message += "{} {}%\r\n".format(user,memory_usage)

            #geting sleeping bustards
            piddata, pidlist = sm.get_idle_pids()
            pidlist.sort(key=lambda ar: -(piddata.get(str(ar)))['memory_info'])
            message += "\r\nTOP IDLE PIDs:\r\n"
            os.system('clear')
            for key in pidlist:
                process = piddata[str(key)]
                datefrom = datetime.fromtimestamp(process['foundtime'])
                seconds = (datetime.now() - datefrom).seconds
                runing_time = "{}h {}m".format(int(seconds / 3600),
                                               int((seconds / 60) % 60))
                message += "user: {}\r\npid: {}\r\npname: {}\r\nRAM: {}G\r\nIDLE: {}\r\n".format(process['username'], process['id'],process['name'],round(process['memory_info'], 2),runing_time)
                #print(process['username'], ' ',
                #      process['id'], ':', process['name'],
                #      ':', process['status'], ':',
                #      round(process['memory_info'], 2),
                #      'GB', datefrom, ':', runing_time)



            if len(message) > 0:
                self.send_message(msg['chat']['id'],message)






t = Telegram()
if t.status:
    print('connected!')
else:
    print('error')


