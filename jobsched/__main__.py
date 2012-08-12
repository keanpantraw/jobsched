#-*- coding: utf-8 -*-
import logging.config

from jobsched.application import app
from jobsched.rest import bp
from jobsched.sched import sched

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

app.config.from_envvar('JOBSCHED_CONFIG')

app.register_blueprint(bp)
sched.configure(app.config.get('SCHED_CONFIG'))
sched.start()

port = app.config.get('JOBSCHED_PORT')
app.run(debug=True, host='0.0.0.0', port=port if port else 58631)
