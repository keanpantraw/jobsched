from ConfigParser import SafeConfigParser
from getopt import getopt
import imp
import os

from uuid import uuid4


def parse_args(args, short_opts, long_opts):
    opts = getopt(args, short_opts, long_opts)
    return dict(opts[0])


def get_option_path(option, opts):
    if option in opts:
        opt = os.path.abspath(opts[option])
        if not os.path.exists(opt):
            raise RuntimeError("No such %s: %s" % (option, opt))
        return opt
    else:
        raise RuntimeError("Specify %s option" % option)


def load_catalog(conf_file, tasks_dir):
    config = SafeConfigParser()
    config.read(conf_file)

    def create_task(section):
        kwargs = dict(config.items(section))
        cls = kwargs.pop('class')
        filename = os.path.basename(kwargs.pop('file'))  # Nobody escape from justice!

        module = imp.load_source(str(uuid4()),
                                 os.path.join(tasks_dir, filename))
        return section, getattr(module, cls)(**kwargs)

    return dict(map(create_task, config.sections()))
