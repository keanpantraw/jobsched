#-*- coding: utf-8 -*-
from apscheduler.job import Job
from apscheduler.scheduler import Scheduler
from collections import namedtuple
from uuid import uuid4

sched = Scheduler()


def list_jobs():
    def job_info(job):
        print job.id
        return {
                "id": str(job.id),
                "name": job.name,
                "interval": str(job.trigger.interval),
                "next_run": str(job.next_run_time)
               }
    return map(job_info, sched.get_jobs())


def schedule_job(task, interval, timeout):
    Info = namedtuple('Info', ['job_id', 'timeout'])
    job_id = uuid4()
    info = Info(job_id=job_id, timeout=timeout)
    job = sched.add_interval_job(task, args=[info], **interval)
    job.id = job_id
    return job_id


def unschedule_job(uuid):
    job = Job()
    job.id = uuid
    return sched.unchedule_job(job)
