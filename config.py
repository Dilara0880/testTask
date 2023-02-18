# DEFAULT_PARAMETERS = [
#     {'name': 'Параметры по умолчанию',
#      'power': 2200,
#      'max_volume': 1.0,
#      'start_temp': 20.0,
#      'end_temp': 100.0,
#      'boiling_time': 10.0,
#      }
# ]

import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'AaJgDjyUYGgz6Qj'
SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, 'app.db')
