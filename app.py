from msilib.schema import Class
import os
import psycopg2
import requests
import re
from flask import Flask, abort, request, render_template
app = Flask(__name__)


class VcronApi:
    VCRON_URL = os.environ.get('VCRON_URL') + \
        '/VisualCron/json/{}?username=' + \
        os.environ.get('VCRON_USER') + \
        '&password=' + \
        os.environ.get('VCRON_PASSWORD') + \
        '&id={}'
    
    @staticmethod
    def __validate_guid(guid):
        GUID_REGEX = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        if not re.fullmatch(GUID_REGEX, guid):
            abort(400)

    @classmethod
    def run_job_url(cls, guid):
        cls.__validate_guid(guid)
        return cls.VCRON_URL.format('Job/Run', guid)

    @classmethod
    def get_job_url(cls, guid):
        cls.__validate_guid(guid)
        return cls.VCRON_URL.format('Job/Get', guid)


@app.route('/')
def index():
    return render_template('index.html')

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

    url = VcronApi.get_job_url(task_guid)
    response = requests.get(url)
    if response.status_code != 200:
        abort(response.status_code)

    response_data = response.json()
    execution_time = response_data.get('Stats')['ExecutionTime']

    url = VcronApi.run_job_url(task_guid)

    vars = request.args.get("variables")
    if vars:
        url += f'&variables={vars}'

    response = requests.get(url)
    if response.status_code != 200:
        abort(response.status_code)
    response_data = response.json()

    status = 'ok'
    if response_data.get('JobStartedResult') != 1:
        status = 'ko'

    return render_template(
        'task.html',
        task_guid=task_guid,
        status=status,
        execution_time=execution_time
    )

@app.route('/status/<task_guid>')
def check_task(task_guid):
    url = VcronApi.get_job_url(task_guid)
    response = requests.get(url)
    if response.status_code != 200:
        abort(response.status_code)

    response_data = response.json()
    if response_data.get('Stats')['Status'] == 0:
        return('Running')
    if response_data.get('Stats')['Status'] == 1:
        if response_data.get('Stats')['ExitCode'] == 0:
            return('Done')
    return('Error')