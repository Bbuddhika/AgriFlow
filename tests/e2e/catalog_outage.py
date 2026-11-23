"""Verify the running foundation's unavailable state and restore market core.

Run after Compose is healthy. This deliberately stops market-core-service,
checks real server-rendered responses, then always attempts to start it again.
Uses synthetic catalog taxonomy only; never removes containers or data volumes.
"""
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
API = os.environ.get('BACKEND_URL', 'http://localhost:8080').rstrip('/')
FRONTEND = os.environ.get('FRONTEND_URL', 'http://localhost:3000').rstrip('/')


def response(url):
    try:
        with urlopen(url, timeout=15) as result:
            return result.status, result.read().decode('utf-8')
    except HTTPError as error:
        return error.code, error.read().decode('utf-8')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def wait_connected(names):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        try:
            status, body = response(FRONTEND)
            if status == 200 and 'Connected to catalog' in body and all(name in body for name in names):
                return
        except (URLError, TimeoutError):
            pass
        time.sleep(2)
    raise AssertionError('Catalog did not reconnect after market core restarted')


def main():
    status, body = response(API + '/api/v1/catalog/produce')
    require(status == 200, 'Baseline catalog unavailable before outage')
    catalog = json.loads(body)
    require(len(catalog) == 6, 'Expected baseline six-item taxonomy')
    names = [item['name'] for item in catalog]
    wait_connected(names)
    try:
        subprocess.run(['docker', 'compose', 'stop', 'market-core-service'], cwd=ROOT, check=True)
        status, body = response(API + '/api/v1/catalog/produce')
        require(status == 503, 'Gateway must report 503 when market core is stopped')
        require(json.loads(body)['title'] == 'Market service unavailable', 'Expected safe upstream error')
        status, body = response(FRONTEND)
        require(status == 200, 'Unavailable page must render successfully')
        require('Connection unavailable' in body and 'The catalog is taking a moment.' in body,
                'Frontend did not show its explicit unavailable state')
        require('Connected to catalog' not in body and 'produce-card' not in body,
                'Unavailable page must not display a connected status or fabricated listings')
        print('PASS: stopped market -> gateway 503 and frontend unavailable without catalog cards', flush=True)
    finally:
        subprocess.run(['docker', 'compose', 'start', 'market-core-service'], cwd=ROOT, check=True)
        wait_connected(names)
        print('PASS: market restored -> all six catalog types render again', flush=True)


if __name__ == '__main__':
    main()
