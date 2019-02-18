import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    APP_DESCRIPTION = 'Calculate Jielong Web App'
    APP_SRV_FILE    = 'hhk_jlcalc.service'
    APP_DIR         = basedir
    APP_BIND_IP     = '0.0.0.0'
    APP_PORT        = 8001
    APP_WORKERS     = 1
    SECRET_KEY      = os.environ.get('SECRET_KEY') or 'you-will-never-cai-dao-ta'

    @classmethod
    def to_dict(cls):
        _dict = {}
        for key in dir(cls):
            if key.isupper():
                _dict[key] = getattr(cls, key)
        return _dict
