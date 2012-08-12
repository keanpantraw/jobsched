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


@contextmanager
def _child_context(child):
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


def _killjob(pid):
    try:
        os.kill(pid, signal.SIGUSR1)
    except OSError:
        pass


def watchdog(timeout=None):
    """Feel my inception
    Taste my C"""
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(self, info, *args, **kwargs):
            parent, child = multiprocessing.Pipe()

            def task(*args, **kwargs):
                with _child_context(child):
                    func(self, info, *args, **kwargs)

            process = multiprocessing.Process(target=task, args=args,
                                            kwargs=kwargs)
            process.start()

            pid = process.pid
            process.join(info.timeout if not timeout else timeout)

            if process.is_alive():
                log.warning("Killed by timeout: %s" % info.job_id)
                _killjob(pid)

            result = parent.recv()
            parent.close()
            log.debug("%s output:\n%s" % (info.job_id, result))
        return wrapped
    return wrapper
