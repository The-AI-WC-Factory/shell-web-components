import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
class GovernanceTests(unittest.TestCase):
    def run_validator(self, event=None, modify=None):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'scaffold';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__'))
            if modify:modify(root)
            env=os.environ.copy();env.pop('GITHUB_EVENT_PATH',None)
            if event is not None:
                path=Path(tmp)/'event.json';path.write_text(json.dumps(event));env['GITHUB_EVENT_PATH']=str(path)
            result=subprocess.run(['python3',str(root/'.github/scripts/validate_governance.py')],env=env,capture_output=True,text=True)
            evidence=json.loads((root/'governance-evidence.json').read_text())
            return result,evidence
    def event(self, fork=False):
        repo='glyad/shell-web-components'
        return {'pull_request':{'head':{'ref':'develop','repo':{'full_name':'fork/repo' if fork else repo}},'base':{'ref':'main','repo':{'full_name':repo}},'title':'chore: promote Phase 0 governance','body':'Refs #1\nPhase 0 governance promotion'}}
    def test_promotion_must_come_from_same_repository(self):
        good,_=self.run_validator(self.event());self.assertEqual(good.returncode,0,good.stderr)
        bad,evidence=self.run_validator(self.event(True));self.assertNotEqual(bad.returncode,0);self.assertFalse(evidence['passed'])
    def test_feature_issue_must_match(self):
        event=self.event();event['pull_request']['head']['ref']='feature/9-test';event['pull_request']['base']['ref']='develop'
        bad,_=self.run_validator(event);self.assertNotEqual(bad.returncode,0)
    def test_yaml_workflow_cannot_hide_unpinned_action(self):
        def modify(root):
            (root/'.github/workflows/unpinned.yaml').write_text('permissions: {}\njobs:\n  test:\n    timeout-minutes: 5\n    steps:\n      - uses: actions/checkout@main\n')
        result,evidence=self.run_validator(modify=modify);self.assertNotEqual(result.returncode,0);self.assertTrue(any('immutable SHA' in x for x in evidence['errors']))
    def test_failure_evidence_survives_missing_or_invalid_input(self):
        for mode in ['LICENSE','.github/ai-dlc.json','invalid-json','implementation']:
            def modify(root):
                if mode=='invalid-json':(root/'.github/ai-dlc.json').write_text('{bad')
                elif mode=='implementation':(root/'package.json').write_text('{}')
                else:(root/mode).unlink()
            result,evidence=self.run_validator(modify=modify);self.assertNotEqual(result.returncode,0);self.assertFalse(evidence['passed']);self.assertTrue(evidence['errors'])

if __name__=='__main__':unittest.main()
