Jobsched - RESTful Job Scheduler
################################

*Jobsched* is a scheduler that allows you easily run periodic tasks on many hosts using just ``curl``.

He allows you to execute any specified scripts or arbitrary python code in designated time intervals.

He comes just with ``Flask`` and ``apscheduler`` dependencies for initial setup.


Installation
============

Easiest way to play with *Jobsched* (works if you have virtualenv):

* ``git clone https://github.com/frenzykryger/jobsched``
* ``cd jobsched``
* ``virtualenv shedenv``
* ``source schedenv/bin/activate``
* ``pip install -r requirements.txt``
* ``./debug.sh``

Now you have *Jobsched*, ready for scheduling!


Configuration
=============

Jobsched require two command line options to start:

- ``--conf-dir`` - directory with all config files

- ``--tasks-dir`` - directory with tasks files


Tasks Catalog
-------------

``catalog.cfg`` specify tasks that will be allowed to run in *Jobsched*

For example, lets look on this configuration:

catalog.cfg ::

        
        [runfoo]
        file=runscript.py
        class=RunScript
        script=foo.bash

        [example]
        file=example.py
        class=ExampleJob
        phrase=foo

        [timeout]
        file=timeout.py
        class=TimeoutJob
        phrase=awwwww

This is ini file with several sections. Each section describe one task.

* *Section name* is a task name
* *file* is name of *python source file* in directory specified by ``--tasks-dir``
* *class* is class name which represents this task in *file*
* other options are arguments which will be passed to ``__init__`` of this *class* 

Example: Task *runfoo* is a class *RunScript* located in *runscript.py*. It accepts argument *script* (that this task will run).


Scheduler configuration
-----------------------

``jobsched.cfg`` is actually a python source file with just three options:

* *JOB_LIVETIME* In seconds. Only applies for jobs that are controlled by watchdog.
* *JOBSCHED_PORT*
* *SCHED_CONFIG* - ``Advanced Python Scheduler`` configuration. Dictionary with any possible scheduler config options. See http://packages.python.org/APScheduler/ for details. For example, here you can tell scheduler to store it's jobs in MySQL, file, sqlite, PostgreSQL, MongoDB. Or you can specify special threadpool for jobs.

By default scheduler store its jobs to a file using *Schelve*.
Adjusting this options should allow you to make persistent jobs (which could be run after *Jobsched* restart), or even run jobs on several hosts. Just like its done with Quartz scheduler.


Logging configuration
---------------------

``logging.cfg`` is just configuration file for ... *logging* module.
Default level is DEBUG and all logs just go to stdout.



Task Scheduling
===============

*Jobsched* provides RESTful interface for job scheduling.


Tasks Catalog
-------------

You allowed only to schedule task that was described in ``catalog.cfg``.
To get current task catalog you need to perform this query: 

``curl -i http://127.0.0.1:58631/catalog`` ::

        
        HTTP/1.0 200 OK
        Content-Type: application/json
        Content-Length: 65
        Server: Werkzeug/0.8.3 Python/2.7.3
        Date: Sun, 12 Aug 2012 23:45:29 GMT

        {
          "tasks": [
                    "runfoo", 
                    "example", 
                    "timeout"
                   ]
        }


As you see, here we have tasks "runfoo", "example" and "timeout".


Schedule A Job
--------------

Currently, only periodic running tasks are supported for scheduling.

To schedule new job you need to perform query like this one:

``curl -iH 'content-type:application/json' -d '{"task":"example","name": "fake", "interval": {"seconds": 1}}' http://127.0.0.1:58631/jobs`` ::
        
        
        HTTP/1.0 202 ACCEPTED
        Content-Type: text/html; charset=utf-8
        Content-Length: 0
        Location: http://127.0.0.1:58631/jobs/22bc4c4e-6749-4e25-b329-4ba0afe07d41
        Server: Werkzeug/0.8.3 Python/2.7.3
        Date: Sun, 12 Aug 2012 23:50:02 GMT

This is a POST query to ``/jobs``.

Query format is ::
        

        {
          "task": "<one of tasks from tasks catalog>",
          "name": "<name of this job>",
          "interval": "<interval between job runs. Job will start not immediately, but after this interval"
        }


Interval format is ::

        
        {
          "seconds": <seconds>,
          "minutes": <minutes>,
          "hours": <hours>,
          "days": <days>,
          "weeks": <weeks>
        }


Any of this interval parameters may be omitted

*Jobsched* will return HTTP 400, if request is malformed.

If scheduling was successful, *Jobsched* will return HTTP 202 and URL to scheduled job in *Location* header.


View Scheduled Job Details
----------------

To view job details you can memorize it's job id or store entire URL from Location header after job scheduling.

You need to perform query like this one:

``curl -i http://127.0.0.1:58631/jobs/2db27b92-d458-41eb-840b-dea280d17fb2`` ::


        HTTP/1.0 200 OK
        Content-Type: application/json
        Content-Length: 140
        Server: Werkzeug/0.8.3 Python/2.7.3
        Date: Mon, 13 Aug 2012 00:15:44 GMT

        {
          "next_run": "2012-08-13 04:15:44.932468", 
          "interval": "0:00:01", 
          "id": "2db27b92-d458-41eb-840b-dea280d17fb2", 
          "name": "fake"
        }

This is GET query to ``/jobs/<uuid>``.


View List of Scheduled Jobs
---------------------------

To view list of scheduled jobs just do GET query to ``/jobs``

Example:

``curl -i http://127.0.0.1:58631/jobs`` ::


        HTTP/1.0 200 OK
        Content-Type: application/json
        Content-Length: 186
        Server: Werkzeug/0.8.3 Python/2.7.3
        Date: Mon, 13 Aug 2012 00:20:18 GMT

        {
          "values": [
                      {
                        "next_run": "2012-08-13 04:20:18.932468", 
                        "interval": "0:00:01", 
                        "id": "2db27b92-d458-41eb-840b-dea280d17fb2", 
                        "name": "fake"
                      }
                    ]
        }


Unschedule Job
--------------

To unschedule job you must send HTTP DELETE to ``/jobs/<uuid>``

For example:

``curl -i -X DELETE http://127.0.0.1:58631/jobs/2db27b92-d458-41eb-840b-dea280d17fb2`` ::
        

        HTTP/1.0 200 OK
        Content-Type: text/html; charset=utf-8
        Content-Length: 0
        Server: Werkzeug/0.8.3 Python/2.7.3
        Date: Mon, 13 Aug 2012 00:23:16 GMT


Create Own Tasks
===============

*Jobsched* comes with runscript.RunScript task that will allow you to execute any script with maximum livetime set to *JOB_LIVETIME*.

But instead, you can execute any arbitrary python code as a job!

To do this, create some file in your ``--task-dir``, for example ``job.py``.

Create a class there ::


        class MyJob(object):
            def __init__(self, **my_parameters):
                """Initialization of your task parameters"""
                pass

            def __call__(self, info):
               """Your job goes here!"""
               pass


Then, just add it to your catalog.cfg ::


        [myGlamorousJob]
        file=job.py
        class=MyJob
        myFineParameter=1
        myBelovedArgument=foo
        theBestFunctionArgumentIeverSeen=3


Restart *Jobsched*.

And viola! Now you can schedule job ``myGlamorousJob``!


Propably you see ``info`` parameter in ``__call__``. It contains your job id and timeout. Maybe you want to manage your job livetime yourself.

Instead you can use ``watchdog`` decorator and he will manage your job execution *for* you!


Just like this ::
        

        from jobsched.watchdog import watchdog


        class MyJob(object):
            def __init__(self, **my_parameters):
                """Initialization of your task parameters"""
                pass

            @watchdog()
            def __call__(self, info):
               """Your job goes here!"""
               pass


And thats all! Now your job will be vicously killed after *JOB_LIVETIME* seconds and you can find what happened in *Jobsched* logs, because watchdog streamed all your job output there.

You think you know better what timeout is desireable for your job?

Not a problem ::


        from jobsched.watchdog import watchdog


        class MyJob(object):
            def __init__(self, **my_parameters):
                """Initialization of your task parameters"""
                pass

            @watchdog(1)
            def __call__(self, info):
               """Your job goes here!"""
               pass


Now your job maximum execution time is set to *1 second*!

This is essentially all that someone might say about *Jobsched*.


Changelog
=========

* *v0.1* - Initial scheduler implementation, watchdog, support for periodic jobs.
