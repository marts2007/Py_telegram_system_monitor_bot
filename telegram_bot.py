import json
from logger import log
import http_fetcher as ht
import system_monitor as sm
from config import config
import time
import socket
import os.path
import psutil

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
                            self.send_message_all(message)
                            drive['alerted'] = 1
                            config.store_config()
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
                message = "Filesystem {} \r\nTotal: %d GiB" % drv.total / (2**30)
                message += "\r\nUsed: %d GiB" % drv.used / (2**30)
                message += "\r\nFree: %d GiB" % drv.free / (2**30)
                if os.path.isfile(drive['report_file']):
                    message += open(drive['report_file'], 'r').read()
                    message += "\r\n\r\n"
            if len(message) > 0:
                self.send_message(msg['chat']['id'],message)


t = Telegram()
if t.status:
    print('connected!')
else:
    print('error')


