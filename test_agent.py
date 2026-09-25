import unittest
from types import SimpleNamespace
from agent import ToolContext, Review, Finding, Evidence, Step, run_agent

def review(quote='价款100元'):
    return Review(summary='草稿',findings=[Finding(title='核查',category='commercial',severity='low',evidence=[Evidence(source_id='d1',quote=quote)],rationale='需确认',suggestion='核查')],missing_information=[],legal_verification_required=[])
class FakeClient:
    def __init__(self,steps): self.steps=iter(steps); self.responses=self
    def parse(self,**kwargs): return SimpleNamespace(output_parsed=next(self.steps))
def step(action,arg='',r=None): return Step(action=action,reason='测试',argument=arg,offset=0,review=r)
class AgentTests(unittest.TestCase):
    def test_unread_and_fabricated_evidence_rejected(self):
        c=ToolContext({'d1':'价款100元'})
        self.assertTrue(c.validate(review()))
        c.call('read_workflow','contract'); c.call('read_document','d1')
        self.assertEqual(c.validate(review()),[])
        self.assertTrue(c.validate(review('价款200元')))
    def test_real_loop_dispatch_and_human_gate(self):
        client=FakeClient([step('read_workflow','contract'),step('read_document','d1'),step('finish',r=review())])
        r=run_agent({'d1':'价款100元'},'采购方',client=client)
        self.assertEqual(len(r['trace']),2)
        self.assertEqual(r['status'],'pending_human_review')
        self.assertFalse(r['legal_sources_verified'])
    def test_limit_does_not_silently_return_success(self):
        c=FakeClient([step('finish',r=review())])
        with self.assertRaises(RuntimeError): run_agent({'d1':'价款100元'},'采购方',client=c,max_steps=1)
    def test_unknown_tool_and_path(self):
        c=ToolContext({'d1':'ok'})
        with self.assertRaises(ValueError): c.call('read_document','/etc/passwd')
        with self.assertRaises(ValueError): c.call('shell','echo hello')
    def test_long_document_coverage_visible(self):
        c=ToolContext({'d1':'a'*7000}); c.call('read_document','d1')
        self.assertTrue(c.unread())
        c.call('read_document','d1',6000); self.assertEqual(c.unread(),[])
if __name__=='__main__': unittest.main()
