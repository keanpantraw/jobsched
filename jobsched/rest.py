from flask import abort
from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request
from flask import make_response
from itertools import ifilter
from urlparse import urljoin

from jobsched.catalog import catalog
from jobsched import sched

bp = Blueprint("API", __name__)


@bp.route('/jobs', methods=['GET'])
def list_jobs():
    return jsonify(**{
                        "values": sched.list_jobs()
                     })


@bp.route('/jobs', methods=['POST'])
def schedule_job():
    task, interval = parse_args()

    if task in catalog:
        interval = filter_interval_args(interval)
        timeout = current_app.config['JOB_LIVETIME']
        job_id = sched.schedule_job(catalog[task], interval, timeout)

        response = make_response('', 202)

        location = get_location(job_id)

        response.headers.add('Location', location)
        return response
    else:
        return error("Task %s not found in catalog" % task), 404


def error(message):
    return jsonify(**{
                       "description": message
                     })


def parse_args():
    data = request.json
    if not data:
        abort(400, error("You must specify task type and interval"))

    task = data.get('task')
    interval = data.get('interval')
    if not interval:
        abort(400, error("You must specify interval"))

    return task, interval


def filter_interval_args(interval):
    acceptable_kwargs = ('weeks', 'days', 'hours', 'minutes', 'seconds')

    return dict(ifilter(lambda (k, v): k in acceptable_kwargs,
                interval.iteritems()))


def get_location(job_id):
    path = '/jobs/%s' % job_id
    return urljoin(request.url, path)


@bp.route('/jobs/<uuid>', methods=['DELETE'])
def unschedule_job(uuid):
    sched.unschedule_job(uuid)
    return 200


@bp.route('/catalog')
def job_catalog():
    return jsonify({
                    "tasks": catalog.keys()
                   })
