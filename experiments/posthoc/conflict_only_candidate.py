"""UNPROMOTED: closed-record-domain conflict-only compiler, offline mechanism.
Keeps all non-conflicting source records; an LLM can only choose within a conflict.
This does NOT understand arbitrary source text or certify source completeness.
"""
import copy, importlib.util, pathlib, unittest
P=pathlib.Path(__file__).resolve().parents[1]/'source_protocol_v1/study.py'
spec=importlib.util.spec_from_file_location('source_study',P)
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)

def build_plan(source):
    records=study.registry(source);groups={};fixed=[]
    for ref,(kind,value) in records.items():
        if kind=='item':key='item:'+value['id']
        elif kind in ('pick','time_limit','cost_limit'):key='rule:'+kind
        else:
            # List constraints cannot be dropped or changed by the choice interface.
            fixed.append(ref);continue
        groups.setdefault(key,[]).append(ref)
    conflicts={}
    for key,refs in groups.items():
        vals={study.canonical(records[r]) for r in refs}
        if len(vals)==1:fixed.append(refs[0])
        else:conflicts[key]=refs
    return {'source':source,'fixed_refs':fixed,'conflicts':conflicts,
            'boundary':'Closed record grammar only; unmodeled prose obligations remain unverified.'}

def apply_choices(plan,choices):
    if not isinstance(choices,dict) or set(choices)!=set(plan['conflicts']):raise ValueError('EXACT_CONFLICT_KEYS_REQUIRED')
    selected=list(plan['fixed_refs'])
    for key,options in plan['conflicts'].items():
        chosen=choices[key]
        if not isinstance(chosen,str) or chosen not in options:raise ValueError('CHOICE_OUTSIDE_CONFLICT')
        selected.append(chosen)
    records=study.registry(plan['source'])
    refs={'item_refs':[r for r in selected if records[r][0]=='item'],
          'rule_refs':[r for r in selected if records[r][0]!='item']}
    compiled=study.assemble(plan['source'],refs)
    return {'spec':compiled,'answer':study.solve(compiled)[0],'selected_refs':refs}

class Tests(unittest.TestCase):
    def test_three_conflict_sources(self):self.assertEqual(sum(bool(build_plan(t['source'])['conflicts']) for t in study.cases()),3)
    def test_no_model_clean(self):
        for t in study.cases():
            p=build_plan(t['source'])
            if not p['conflicts']:self.assertEqual(apply_choices(p,{})['spec'],study.normalize(t['gold']))
    def test_known_source_choices(self):
        choices={'S03':{'item:A':'L04'},'S04':{'rule:time_limit':'R04'},'S05':{'item:A':'L01'}}
        for t in study.cases():
            if t['id'] in choices:self.assertEqual(apply_choices(build_plan(t['source']),choices[t['id']])['spec'],study.normalize(t['gold']))
    def test_cannot_delete_constraint(self):
        p=build_plan(study.cases()[5]['source'])
        with self.assertRaises(ValueError):apply_choices(p,{'drop':'R04'})
    def test_cannot_change_number(self):
        p=build_plan(study.cases()[2]['source'])
        with self.assertRaises(ValueError):apply_choices(p,{'item:A':999})
    def test_cannot_choose_unrelated(self):
        p=build_plan(study.cases()[2]['source'])
        with self.assertRaises(ValueError):apply_choices(p,{'item:A':'L02'})
    def test_wrong_applicability_not_certified(self):
        t=study.cases()[2];p=build_plan(t['source'])
        wrong=apply_choices(p,{'item:A':'L01'})
        self.assertNotEqual(wrong['spec'],study.normalize(t['gold']))
        self.assertFalse(study.score_answer(t['gold'],wrong['answer']))
    def test_missing_choice_closed(self):
        with self.assertRaises(ValueError):apply_choices(build_plan(study.cases()[2]['source']),{})

if __name__=='__main__':unittest.main()
