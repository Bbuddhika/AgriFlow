"""Validate service layout and planning coverage without external dependencies."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
NS = {'m': 'http://maven.apache.org/POM/4.0.0'}


def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)


parent = ET.parse(ROOT / 'backend/pom.xml').getroot()
modules = [n.text for n in parent.findall('m:modules/m:module', NS)]
services = ['api-gateway', 'auth-iam-service', 'market-core-service',
            'notification-service', 'analytics-ai-service']
require(set(modules) == {'common-contracts', *services}, 'Unexpected Maven modules')
require(parent.findtext('m:packaging', namespaces=NS) == 'pom', 'Parent must aggregate')
for module in modules:
    base = ROOT / 'backend' / module
    pom = ET.parse(base / 'pom.xml').getroot()
    require(pom.findtext('m:artifactId', namespaces=NS) == module, module + ' artifact')
    require(pom.findtext('m:parent/m:relativePath', namespaces=NS) == '../pom.xml', module + ' parent')
    if module in services:
        for filename in ['Dockerfile', 'src/main/resources/application.yml']:
            require((base / filename).is_file(), module + ' missing ' + filename)
        require(list(base.glob('src/main/java/**/*Application.java')), module + ' entry point')
        docker = (base / 'Dockerfile').read_text(encoding='utf-8')
        require(f'-pl {module} -am' in docker, module + ' Docker build selection')
        if module != 'api-gateway':
            require((base / 'src/main/resources/db/migration').is_dir(), module + ' migration ownership')
require(not (ROOT / 'backend/src').exists(), 'Obsolete root backend src remains')
require(not (ROOT / 'backend/Dockerfile').exists(), 'Obsolete backend Dockerfile remains')
test = ROOT / 'backend/market-core-service/src/test/java/lk/agriflow/CatalogIntegrationTest.java'
require(test.read_text(encoding='utf-8').count('@Test\n') == 5, 'Preserve original five integration methods')

with (ROOT / 'docs/testing/requirements-traceability.csv').open(encoding='utf-8', newline='') as f:
    trace = list(csv.DictReader(f))
with (ROOT / 'docs/development/work-board.csv').open(encoding='utf-8', newline='') as f:
    board = list(csv.DictReader(f))
expected = {f'FR{i:02}' for i in range(1, 23)} | {f'NFR-{i:02}' for i in range(1, 11)}
expected |= {f'NEG{i:02}' for i in range(1, 8)} | {'ROLE01', 'ROLE02'}
require({r['RequirementID'] for r in trace} == expected, 'Requirement trace coverage')
require(len(trace) == len(expected), 'Duplicate trace requirement')
require({r['RequirementID'] for r in board} == expected, 'Work board requirement coverage')
require(len(board) == len(expected), 'Duplicate work board requirement')
for row in trace:
    require(row['Services'] and row['Modules'] and row['ProposedTestNames_NOT_EXISTING_TEST_CLAIMS'], row['RequirementID'] + ' ownership/test mapping')
    require(all(s in services for s in row['Services'].split(';')), row['RequirementID'] + ' unknown service')
for row in board:
    require(row['ExpectedBehavior'] and row['AcceptanceEvidence'], row['RequirementID'] + ' acceptance detail')

# Check local Markdown links in current planning documents; historical outputs are excluded.
for doc in [ROOT / 'README.md', ROOT / 'backend/README.md', *sorted((ROOT / 'docs/development').glob('*.md')),
            ROOT / 'docs/folder-structure.md', ROOT / 'docs/architecture/003-separate-backend-services.md']:
    for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
        if '://' in link or link.startswith('#'):
            continue
        require((doc.parent / link.split('#')[0]).exists(), f'Broken link: {doc.relative_to(ROOT)} -> {link}')

paths = ['.env', 'frontend/.env.local', 'docs/.browser-profile/state',
         'docs/.chrome-profile/state', '.cache/probe', 'backend/auth-iam-service/target/probe']
git = ['git', '-c', 'safe.directory=' + ROOT.as_posix()]
result = subprocess.run(git + ['check-ignore', '--stdin', '-z'],
                        input=('\0'.join(paths) + '\0').encode(), capture_output=True, cwd=ROOT)
ignored = set(result.stdout.decode().rstrip('\0').split('\0'))
require(result.returncode == 0 and ignored == set(paths),
        'Private/generated exclusions; missing: ' + str(set(paths) - ignored) + result.stderr.decode())
print(f'PASS: {len(services)} services + common contracts; 5 preserved integration methods; '
      f'{len(trace)} requirements mapped to stories, services and proposed tests; planning links; private/generated exclusions')
print('Scope: static Stage 00 checks only; no application runtime or business acceptance claimed.')

if '--compose' in sys.argv:
    environment = os.environ.copy()
    for key in ['POSTGRES_PASSWORD', 'RABBITMQ_PASSWORD', 'IDENTITY_DB_PASSWORD',
                'NOTIFICATION_DB_PASSWORD', 'ASSISTANT_DB_PASSWORD']:
        environment[key] = 'configuration-check-only'
    config = subprocess.run(['docker', 'compose', '--env-file', '.env.example', 'config', '--format', 'json'],
                            capture_output=True, text=True, cwd=ROOT, env=environment)
    require(config.returncode == 0, 'Compose configuration: ' + config.stderr)
    compose = json.loads(config.stdout)
    configured = compose['services']
    databases = {'market-core-service': 'database', 'auth-iam-service': 'identity-database',
                 'notification-service': 'notifications-database', 'analytics-ai-service': 'assistant-database'}
    require(set(configured) == {*services, *databases.values(), 'rabbitmq', 'frontend'}, 'Compose container coverage')
    require(configured['frontend']['environment']['API_BASE_URL'] == 'http://api-gateway:8080', 'Frontend gateway target')
    for name, service in configured.items():
        require(service['image'].startswith('dambulla-agriflow-'), name + ' image name')
        require(service.get('healthcheck'), name + ' healthcheck')
        if name in services:
            require(service['build']['dockerfile'] == name + '/Dockerfile', name + ' Dockerfile')
            require(Path(service['build']['context']).resolve() == ROOT / 'backend', name + ' build context')
        if name not in ['api-gateway', 'frontend', 'rabbitmq']:
            require(not service.get('ports'), name + ' must not expose host ports')
        for port in service.get('ports', []):
            require(port.get('host_ip') == '127.0.0.1', name + ' host bind')
            if name == 'rabbitmq': require(port['target'] == 15672, 'AMQP must remain private')
    for owner, database in databases.items():
        data_networks = set(configured[database]['networks'])
        require(len(data_networks) == 1, database + ' isolated data network')
        clients = {name for name, cfg in configured.items() if data_networks & set(cfg['networks'])}
        require(clients == {owner, database}, database + ' exclusive service ownership')
    print('PASS: Compose configuration; 11 containers; owned database networks; service Dockerfiles; loopback host ports')
