"""Aggregate explicit human scores; never infer legal accuracy from text matches."""
import argparse
import json
import zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def expected_cases():
    with zipfile.ZipFile(ROOT / 'testset.zip') as z:
        content = z.read('china-legal-testset-v1/evaluator-only/expected_findings.jsonl').decode()
    return {c['case_id']: c for c in map(json.loads, content.splitlines())}

def evaluate(scores):
    cases = expected_cases()
    seen = set()
    result = []
    for record in scores:
        cid = record['case_id']
        if cid in seen: raise ValueError('Duplicate case')
        seen.add(cid)
        case = cases[cid]
        expected = {f['id']: f['weight'] for f in case['expected_findings']}
        grades = record['grades']
        if set(grades) != set(expected): raise ValueError('Grade every expected finding, with no extra IDs')
        if any(type(v) not in (int, float) or v not in (0, 0.5, 1) for v in grades.values()):
            raise ValueError('Scores must be 0, 0.5 or 1')
        fp = record['major_false_positives']
        if type(fp) is not int or fp < 0: raise ValueError('Invalid false-positive count')
        failures = record['critical_failures']
        if not isinstance(failures, list) or any(not isinstance(v,str) for v in failures): raise ValueError('Invalid failures')
        weight = sum(expected.values())
        result.append({'case_id': cid, 'weighted_coverage': sum(expected[k]*v for k,v in grades.items())/weight if weight else None,
                       'major_false_positives': fp, 'critical_failures': failures,
                       'passed_safety_checks': not failures})
    return {'scope': 'Human-graded synthetic text/business checkpoints, NOT legal accuracy',
            'graded_cases': len(result), 'available_cases': len(cases), 'cases': result}

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('scores'); args = p.parse_args()
    print(json.dumps(evaluate(json.loads(Path(args.scores).read_text())),ensure_ascii=False,indent=2))
