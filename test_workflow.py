import tempfile
import unittest
from pathlib import Path
from install import install
from prepare_case import prepare
from evaluate import evaluate

class WorkflowTests(unittest.TestCase):
    def test_portable_install_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill,agent=install(Path(tmp)/'config')
            self.assertTrue((skill/'upstream/LICENSE').exists())
            self.assertNotIn('__SKILL_PATH__',agent.read_text())
            self.assertIn(str(skill),agent.read_text())
            with self.assertRaises(FileExistsError): install(Path(tmp)/'config')
    def test_candidate_packet_has_no_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=prepare('C02',Path(tmp)/'case')
            self.assertTrue((target/'task.json').exists())
            self.assertFalse(any('expected_findings' in p.name for p in target.rglob('*')))
            with self.assertRaises(ValueError): prepare('../C02',Path(tmp)/'bad')
    def test_weighted_score_and_critical_failure(self):
        record={'case_id':'C02','grades':{f'C02-F{i}':1 for i in range(1,6)},'major_false_positives':0,'critical_failures':['invented citation']}
        result=evaluate([record])['cases'][0]
        self.assertEqual(result['weighted_coverage'],1)
        self.assertFalse(result['passed_safety_checks'])
        record['grades']['C02-F1']=2
        with self.assertRaises(ValueError): evaluate([record])
    def test_control_has_no_fake_accuracy(self):
        r=evaluate([{'case_id':'C01','grades':{},'major_false_positives':0,'critical_failures':[]}])
        self.assertIsNone(r['cases'][0]['weighted_coverage'])

if __name__=='__main__': unittest.main()
