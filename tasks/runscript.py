from jobsched.watchdog import watchdog

import os
import subprocess
import sys


class RunScript(object):
    def __init__(self, script=None):
        self.script = os.path.abspath(script)

    @watchdog()
    def __call__(self, info):
        if os.path.exists(self.script):
            script = os.path.abspath(self.script)
            p = subprocess.Popen([script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while p.poll() is None:
                sys.stdout.write(p.stdout.readline())
            sys.stdout.write(p.stdout.read())
            if p.returncode:
                raise RuntimeError("Script %s terminated "
                                   "with status %d" % (script, p.returncode))
        else:
            raise RuntimeError("No such script, %s" % self.script)
