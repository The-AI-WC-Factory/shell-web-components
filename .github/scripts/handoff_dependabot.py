"""AI-operated dependency handoff. Never execute a dependency PR's code.

Run with an authenticated GitHub CLI: python3 handoff_dependabot.py PR_NUMBER.
Creates an Issue, compliant feature branch, draft PR and native Issue link.
An AI operator then verifies CI, requests Copilot review and marks it ready.
"""
import argparse
import json
import subprocess

REPO = 'glyad/shell-web-components'


def api(path, body=None, method='POST'):
    args = ['gh', 'api', path]
    if body is not None:
        args += ['-X', method, '--input', '-']
    return json.loads(subprocess.check_output(
        args, input=json.dumps(body) if body is not None else None, text=True))


def validate_candidate(pr, comparison, files):
    if not (pr['state'] == 'open' and pr['user']['login'] == 'dependabot[bot]'
            and pr['user']['type'] == 'Bot' and pr['base']['ref'] == 'develop'
            and (pr['head']['repo'] or {}).get('full_name') == REPO):
        raise ValueError('Only open, same-repository Dependabot candidates for develop are accepted')
    if comparison['behind_by'] != 0 or comparison['merge_base_commit']['sha'] != pr['base']['sha']:
        raise ValueError('Candidate must be updated to current develop before handoff')
    if not files or any(f['status'] != 'modified' or not f['filename'].startswith('.github/workflows/')
                        or not f['filename'].endswith(('.yml', '.yaml')) for f in files):
        raise ValueError('Only modified Actions workflow files are allowed in this handoff')


def handoff(number, dry_run=False):
    root = f'repos/{REPO}'
    pr = api(f'{root}/pulls/{number}')
    comparison = api(f"{root}/compare/{pr['base']['sha']}...{pr['head']['sha']}")
    files = []
    page = 1
    while True:
        batch = api(f'{root}/pulls/{number}/files?per_page=100&page={page}')
        files.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    if len(files) != pr['changed_files']:
        raise ValueError('GitHub did not return the complete candidate diff; refuse handoff')
    validate_candidate(pr, comparison, files)
    marker = f'Dependency candidate #{number}'
    page = 1
    while True:
        issues = api(f'{root}/issues?state=all&per_page=100&page={page}')
        if any(i['title'] == marker for i in issues):
            raise ValueError('A handoff Issue already exists; resume it instead of creating a duplicate')
        if len(issues) < 100:
            break
        page += 1
    if dry_run:
        return {'candidate': number, 'base': pr['base']['sha'], 'head': pr['head']['sha'],
                'files': [f['filename'] for f in files], 'mutation': False}
    # Recheck both refs before creating any resources.
    fresh = api(f'{root}/pulls/{number}')
    if (fresh['head']['sha'], fresh['base']['sha']) != (pr['head']['sha'], pr['base']['sha']):
        raise ValueError('Candidate changed during preflight; retry')
    validate_candidate(fresh, comparison, files)
    issue = api(f'{root}/issues', {'title': marker,
        'body': f'AI dependency maintenance from {pr["html_url"]}.\n\nAcceptance: native Issue-linked feature PR, pinned Actions, passing governance, current-head independent AI approval and gated merge. Close the original candidate only after the feature PR merges.'})
    branch = f'feature/{issue["number"]}-dependency-update'
    # Candidate SHA is a verified descendant of current develop; preserve its history.
    api(f'{root}/git/refs', {'ref': f'refs/heads/{branch}', 'sha': pr['head']['sha']})
    proposed = api(f'{root}/pulls', {'title': f'chore: apply dependency candidate #{number}',
        'head': branch, 'base': 'develop', 'draft': True,
        'body': f'Refs #{issue["number"]}\n\nAI-operated dependency handoff from {pr["html_url"]}. No candidate code was executed. Obtain passing governance and independent AI approval before merge.'})
    result = api('graphql', {'query': 'mutation($issue:ID!,$prs:[ID!]!){ addCloseIssueReferences(input:{issueId:$issue,pullRequestIds:$prs}) { clientMutationId } }',
        'variables': {'issue': issue['node_id'], 'prs': [proposed['node_id']]}})
    if result.get('errors'):
        raise RuntimeError('Native Issue link failed; keep the draft and repair the link')
    return {'issue': issue['html_url'], 'pull_request': proposed['html_url'],
            'branch': branch, 'candidate': pr['html_url'], 'mutation': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    print(json.dumps(handoff(args.number, args.dry_run), indent=2))
