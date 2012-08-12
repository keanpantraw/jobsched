#-*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser
from getopt import getopt
import logging.config
import os
import sys

from jobsched.application import app
from jobsched.rest import bp
from jobsched.sched import sched


opts = getopt(sys.argv[1:], ['c'], ['conf-dir='])
opts = (opt for opt in opts if len(opt) == 1)
opts = (opt[0] for opt in opts)
opts = dict(opts)

if '--conf-dir' in opts:
    conf_dir = os.path.abspath(opts['--conf-dir'])
else:
    raise RuntimeError("Specify --conf-dir option")

if not os.path.exists(conf_dir):
    raise RuntimeError("No such --conf-dir: %s" % conf_dir)


def load_catalog(conf_file):
    import jobsched.jobs
    config = SafeConfigParser()
    config.read(conf_file)

    def create_task(section):
        kwargs = dict(config.items(section))
        cls = kwargs.pop('class')
        return section, getattr(jobsched.jobs, cls)(**kwargs)

    return dict(map(create_task, config.sections()))


logging.config.fileConfig(os.path.join(conf_dir, 'logging.conf'),
                          disable_existing_loggers=False)

app.config.from_pyfile(os.path.join(conf_dir, 'jobsched.cfg'))

app.register_blueprint(bp)
sched.configure(app.config.get('SCHED_CONFIG'))
sched.start()

app.config['catalog'] = load_catalog(os.path.join(conf_dir, 'catalog.cfg'))

port = app.config.get('JOBSCHED_PORT')
app.run(debug=True, host='0.0.0.0', port=port if port else 58631)
