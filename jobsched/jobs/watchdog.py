from contextlib import contextmanager
from cStringIO import StringIO
import functools
import logging
import multiprocessing
import os
import signal
import sys
import traceback

log = logging.getLogger(__name__)
log.propagate = True


class Watchdog(object):
    """Feel my inception
       Taste my C"""
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype):
        """Make Watchdog a descriptor"""
        return functools.partial(self.__call__, obj)

    @contextmanager
    def child_context(self, child):
        output = StringIO()

        def close_pipe(signum=None, frame=None):
            result = output.getvalue()
            child.send(result)
            child.close()
            sys.exit(0)

        sys.stdout = output
        sys.stderr = output
        signal.signal(signal.SIGUSR1, close_pipe)

        try:
            yield
        except:
            traceback.print_exc()
        finally:
            close_pipe()

    def kill(self, pid):
        try:
            os.kill(pid, signal.SIGUSR1)
        except OSError:
            pass

    def __call__(self, itself, info, *args, **kwargs):
        parent, child = multiprocessing.Pipe()

        def task(info, *args, **kwargs):
            with self.child_context(child):
                self.func(itself, info, *args, **kwargs)

        process = multiprocessing.Process(target=task, args=[info],
                                        kwargs=kwargs)
        process.start()

        pid = process.pid
        process.join(info.timeout)

        if process.is_alive():
            log.warning("Killed by timeout: %s" % info.job_id)
            self.kill(pid)

        result = parent.recv()
        parent.close()
        log.debug("%s output:\n%s" % (info.job_id, result))
