import json
from logger import log

# loaded config
default_conf = {
        'apikey': '',
        'user_list': [],
        'drives': [  # drives to monitor
            {
                'path': '/',
                'maxusage': 95,
                'report_file': 'datadrive.log',
                'alerted': 0,
                'exceeded':0,
            },

        ],
        'sleeping_pids' : {}
        ,
        'proxies': {
            "https": "http://192.168.0.3:8118"
            # remove this line if you do not need proxy
        },
        'lastupdate_id': 0
    }
# Read data from file:
try:
    conf = json.load(open("config.json"))
except Exception as e:
    log('Config load failed')
    conf = default_conf


class Config(object):

    def __init__(self):
        self._config = conf  # set it to conf

    def __getattr__(self, name):
        return self.get_property(name)

    def change(self, name, value):
        self._config[name] = value
        self.store_config()

    def _config(self, name, value):
        self._config[name] = value

    def get_property(self, property_name: str):
        if property_name not in self._config.keys():  # we don't want KeyError
            if property_name in default_conf:
                return default_conf[property_name]
            return None  # just return None if not found
        return self._config[property_name]

    def store_config(self):
        json.dump(self._config, open("config.json", 'w'))


config = Config()
