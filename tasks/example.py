from time import sleep


class ExampleJob(object):
    def __init__(self, phrase=None):
        self.foo = phrase

    def __call__(self, info):
        print self.foo
        sleep(2)
