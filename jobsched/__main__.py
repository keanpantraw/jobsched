#-*- coding: utf-8 -*-
import logging.config
import os
import sys

from jobsched.application import app
from jobsched import conf
from jobsched.rest import bp
from jobsched.sched import sched


options = conf.parse_args(sys.argv[1:], ['ct'], ['conf-dir=', 'tasks-dir='])

conf_dir = conf.get_option_path('--conf-dir', options)
tasks_dir = conf.get_option_path('--tasks-dir', options)

logging.config.fileConfig(os.path.join(conf_dir, 'logging.conf'),
                          disable_existing_loggers=False)

app.config.from_pyfile(os.path.join(conf_dir, 'jobsched.cfg'))

app.register_blueprint(bp)
sched.configure(app.config.get('SCHED_CONFIG'))
sched.start()

catalog_file = os.path.join(conf_dir, 'catalog.cfg')
app.config['catalog'] = conf.load_catalog(catalog_file, tasks_dir)

port = app.config.get('JOBSCHED_PORT')
app.run(debug=True, host='0.0.0.0', port=port if port else 58631)
