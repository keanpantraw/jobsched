from jobsched.jobs.watchdog import Watchdog

import os
import subprocess
import sys


class RunScript(object):
    def __init__(self, script):
        self.script = os.path.abspath(script)

    @Watchdog
    def __call__(self, info):
        if os.path.exists(self.script):
            script = os.path.abspath(self.script)
            p = subprocess.Popen([script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, = p.communicate()
            while p.poll() is None:
                sys.stdout.write(stdout.readline())
            sys.stdout(stdout.read())
            if p.returncode:
                raise RuntimeError("Script %s terminated "
                                   "with status %d" % (script, p.returncode))
        else:
            raise RuntimeError("No such script, %s" % self.script)
