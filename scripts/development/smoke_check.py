"""Check the running stack using only the Python standard library."""
import json
import os
from urllib.request import urlopen

backend = os.environ.get('BACKEND_URL', 'http://localhost:8080')
frontend = os.environ.get('FRONTEND_URL', 'http://localhost:3000')


def read(url):
    with urlopen(url, timeout=15) as response:
        assert response.status == 200, url
        return response.read().decode('utf-8')


system = json.loads(read(backend + '/api/v1/system'))
assert system['stage'] == 'foundation'
assert json.loads(read(backend + '/actuator/health/readiness'))['status'] == 'UP'
catalog = json.loads(read(backend + '/api/v1/catalog/produce'))
assert len(catalog) == 6, 'Expected the initial catalog migration'
assert {item['unit'] for item in catalog} == {'kg'}
page = read(frontend)
assert 'Connected to catalog' in page, 'Frontend did not reach the backend'
assert all(item['name'] in page for item in catalog), 'Catalog not rendered'
print('PASS: gateway readiness, catalog API and frontend integration; dependency health checked by Compose --wait')
