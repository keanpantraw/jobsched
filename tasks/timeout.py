from jobsched.watchdog import watchdog
from time import sleep


class TimeoutJob(object):
    def __init__(self, phrase=None):
        self.foo = phrase

    @watchdog(1)
    def __call__(self, info):
        print self.foo
        sleep(2)
