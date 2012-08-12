from flask import abort
from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request
from flask import make_response
from itertools import ifilter
from urlparse import urljoin

from jobsched import sched

bp = Blueprint("API", __name__)


@bp.route('/jobs', methods=['GET'])
def list_jobs():
    return jsonify(**{
                        "values": sched.list_jobs()
                     })


@bp.route('/jobs/<uuid>', methods=['GET'])
def get_job(uuid):
    for job in sched.list_jobs():
        if job['id'] == uuid:
            return jsonify(**job), 200
    return error('No job with id %s found' % uuid), 404


@bp.route('/jobs', methods=['POST'])
def schedule_job():
    name, task, interval = parse_args()

    catalog = current_app.config.get('catalog', {})

    if task in catalog:
        interval = filter_interval_args(interval)
        timeout = current_app.config['JOB_LIVETIME']
        job_id = sched.schedule_job(name, catalog[task], interval, timeout)

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

    name = data.get('name')
    task = data.get('task')
    interval = data.get('interval')
    if not name:
        abort(400, error("You must specify name"))
    if not task:
        abort(400, error("You must specify task"))
    if not interval:
        abort(400, error("You must specify interval"))

    return name, task, interval


def filter_interval_args(interval):
    acceptable_kwargs = ('weeks', 'days', 'hours', 'minutes', 'seconds')

    interval = dict(ifilter(lambda (k, v): k in acceptable_kwargs,
                    interval.iteritems()))

    if not interval:
        abort(400, error("You must specify interval"))
    return interval


def get_location(job_id):
    path = '/jobs/%s' % job_id
    return urljoin(request.url, path)


@bp.route('/jobs/<uuid>', methods=['DELETE'])
def unschedule_job(uuid):
    if not sched.unschedule_job(uuid):
        return error('No job with id %s found' % uuid), 404
    return "", 200


@bp.route('/catalog')
def job_catalog():
    return jsonify({
                    "tasks": current_app.config.get('catalog', {}).keys()
                   })
