import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('handoff',Path(__file__).resolve().parents[1]/'.github/scripts/handoff_dependabot.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.pr={'state':'open','user':{'login':'dependabot[bot]','type':'Bot'},'base':{'ref':'develop','sha':'base'},'head':{'repo':{'full_name':h.REPO},'sha':'candidate'},'changed_files':1,'html_url':'https://example.test/pr/3'}
        self.calls=[];self.reads=0;self.final_change={}
    def api(self,path,body=None,method='POST'):
        self.calls.append((path,body))
        if '/compare/' in path:return {'behind_by':0,'merge_base_commit':{'sha':'base'}}
        if '/files?' in path:return [{'filename':'.github/workflows/governance.yml','status':'modified'}]
        if '/issues?' in path:return []
        if path.endswith('/pulls/3'):
            self.reads+=1;p=copy.deepcopy(self.pr)
            if self.reads>1:p.update(self.final_change)
            return p
        if path.endswith('/issues'):return {'number':8,'node_id':'issue8','html_url':'https://example.test/issue/8'}
        if path.endswith('/git/commits/candidate'):return {'tree':{'sha':'tree'}}
        if path.endswith('/git/commits'):return {'sha':'distinct-handoff'}
        if path.endswith('/git/refs'):return {}
        if path.endswith('/pulls'):return {'node_id':'pr8','html_url':'https://example.test/pr/8'}
        if path=='graphql':return {'data':{}}
        raise AssertionError(path)
    def test_distinct_commit_preserves_candidate_tree_and_history(self):
        with patch.object(h,'api',self.api):h.handoff(3)
        commit=next(b for p,b in self.calls if p.endswith('/git/commits'))
        self.assertEqual(commit['tree'],'tree');self.assertEqual(commit['parents'],['candidate'])
        branch=next(b for p,b in self.calls if p.endswith('/git/refs'))
        self.assertEqual(branch['sha'],'distinct-handoff')
        self.assertTrue(any(p=='graphql' and b['variables']['issue']=='issue8' for p,b in self.calls))
    def test_closed_or_retargeted_candidate_creates_nothing(self):
        for change in [{'state':'closed'},{'base':{'sha':'base','ref':'main'}}]:
            with self.subTest(change=change):
                self.reads=0;self.calls=[];self.final_change=change
                with patch.object(h,'api',self.api):
                    with self.assertRaises(ValueError):h.handoff(3)
                self.assertTrue(all(b is None for _,b in self.calls))
    def test_dry_run_creates_nothing(self):
        with patch.object(h,'api',self.api):self.assertFalse(h.handoff(3,True)['mutation'])
        self.assertTrue(all(b is None for _,b in self.calls))

if __name__=='__main__':unittest.main()
