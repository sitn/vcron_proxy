import os
import psycopg2
import requests
from flask import Flask, abort, request
app = Flask(__name__)

vcron_url = os.environ.get('VCRON_URL') + \
    '/VisualCron/json/Job/Run?username=' + \
    os.environ.get('VCRON_USER') + \
    '&password=' + \
    os.environ.get('VCRON_PASSWORD') + \
    '&id='

@app.route('/')
def index():
    return 'Bienvenue'

@app.route('/run/<task_name>')
def run_task(task_name):
    # read routes
    conn = psycopg2.connect(
        host=os.environ.get('PGHOST', 'localhost'),
        port=os.environ.get('PGPORT', 5432),
        dbname=os.environ.get('PGDATABASE', 'vcron_proxy'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT vcron_guid FROM routes WHERE url = %s", [task_name])
    route = cur.fetchone()
    cur.close()
    conn.close()

    if not route:
        abort(404)
    task_guid = route[0]

    url = f'{vcron_url}{task_guid}'
    vars = request.args.get("variables")
    if vars:
        url += f'&variables={vars}'

    response = requests.get(url)
    if response.status_code != 200:
        abort(response.status_code)
    response_data = response.json()
    if response_data.get('JobStartedResult') != 1:
        abort(404, f'The job with id {task_guid} job does not exist or cannot be run.')

    return 'Ok'
