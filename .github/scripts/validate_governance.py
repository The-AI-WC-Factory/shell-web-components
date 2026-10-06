"""Deterministic Phase 0 contract checks; no third-party dependencies."""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

required = ['README.md', 'LICENSE', 'AGENTS.md', 'CONTRIBUTING.md', 'SECURITY.md',
            'docs/product-charter.md', 'docs/governance.md', 'docs/releases.md',
            '.github/ai-dlc.json', '.github/PULL_REQUEST_TEMPLATE.md',
            '.github/dependabot.yml', '.github/ISSUE_TEMPLATE/config.yml']
for name in required:
    require((ROOT / name).is_file(), f'Missing {name}')

def write_evidence(phase=None):
    evidence = {'phase': phase, 'commit': os.environ.get('GITHUB_SHA', 'local'),
                'run_id': os.environ.get('GITHUB_RUN_ID'), 'passed': not errors,
                'checks': ['required-files', 'ai-only-contract', 'MIT', 'phase-boundary', 'workflow-pins', 'git-flow'],
                'errors': errors, 'component_tests': 'not applicable: no components implemented'}
    (ROOT / 'governance-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')

if errors:
    write_evidence()
    raise SystemExit('\n'.join(errors))
try:
    policy = json.loads((ROOT / '.github/ai-dlc.json').read_text())
    if not isinstance(policy, dict):
        raise ValueError('Policy must be a JSON object')
except (ValueError, OSError) as error:
    errors.append(f'Cannot read governance policy: {error}')
    write_evidence()
    raise SystemExit('\n'.join(errors))
require(policy.get('human_role') == 'product_management_only', 'Human role must be product management only')
require(policy.get('engineering_operator') == 'ai_only', 'Engineering must be AI-operated')
require(policy.get('license') == 'MIT' and policy.get('git_flow') is True, 'MIT and Git Flow are required')
license_text = (ROOT / 'LICENSE').read_text()
require('MIT License' in license_text and 'Permission is hereby granted' in license_text, 'MIT license missing')

if policy.get('phase') == 0:
    for path in ['src', 'components', 'packages', 'examples', 'demo', 'dist', 'package.json']:
        require(not (ROOT / path).exists(), f'Implementation is out of Phase 0 scope: {path}')

for workflow in sorted(p for p in (ROOT / '.github/workflows').iterdir() if p.suffix in {'.yml', '.yaml'}):
    body = workflow.read_text()
    require('pull_request_target:' not in body, f'Unsafe PR target trigger: {workflow.name}')
    require('permissions:' in body, f'Explicit permissions missing: {workflow.name}')
    require('timeout-minutes:' in body, f'Timeout missing: {workflow.name}')
    for action in re.findall(r'uses:\s*([^\s#]+)', body):
        require(bool(re.fullmatch(r'[^@]+@[0-9a-f]{40}', action)), f'Action must use immutable SHA: {action}')

event_path = os.environ.get('GITHUB_EVENT_PATH')
event = json.loads(Path(event_path).read_text()) if event_path else {}
pr = event.get('pull_request')
if pr:
    head, base = pr['head']['ref'], pr['base']['ref']
    body, title = pr.get('body') or '', pr.get('title') or ''
    linked = bool(re.search(r'(?i)\b(?:refs|closes|fixes|resolves)\s+#\d+\b', body))
    require(linked, 'PR must reference an Issue using Refs #N or a closing keyword')
    feature = bool(re.fullmatch(r'feature/\d+-[a-z0-9][a-z0-9-]*', head))
    hotfix = bool(re.fullmatch(r'hotfix/\d+-[a-z0-9][a-z0-9-]*', head))
    release = bool(re.fullmatch(r'release/\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?', head))
    promotion = (policy.get('phase') == 0 and head == 'develop' and base == 'main'
                 and title == 'chore: promote Phase 0 governance'
                 and 'Phase 0 governance promotion' in body)
    valid = ((base == 'develop' and (feature or release or hotfix))
             or (base == 'main' and (release or hotfix or promotion))
             or (base.startswith(('release/', 'hotfix/')) and (feature or hotfix)))
    require(valid, f'Invalid Git Flow route {head} -> {base}')
    if feature:
        issue = head.split('/')[1].split('-')[0]
        require(bool(re.search(rf'(?i)\b(?:refs|closes|fixes|resolves)\s+#{issue}\b', body)),
                'Feature branch Issue number must match PR reference')

write_evidence(policy.get('phase'))
if errors:
    raise SystemExit('\n'.join(errors))
print('Phase 0 governance checks passed; component testing is not yet applicable.')
