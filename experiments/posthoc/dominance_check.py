#!/usr/bin/env python3
"""Post-hoc input-only objective witness, not a global optimality certificate.
Only the fixed selected-ID combinatorial contract is supported. No model calls,
no gold oracle, no implicit source extraction, no automatic answer mutation.
"""
from __future__ import annotations
import hashlib, itertools, json, unittest, pathlib, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"autolab_v1"))
from run import constraints


def check(task: dict, selected: list[str]) -> dict:
    if not isinstance(selected,list) or any(not isinstance(x,str) for x in selected):
        return {'status':'NOT_APPLICABLE','reason':'selected must be an ID array'}
    errors, old=constraints(task,selected)
    if errors:
        return {'status':'NOT_APPLICABLE','reason':'candidate is infeasible','violations':errors}
    ids={x['id'] for x in task['items']}; chosen=set(selected)
    best=None; tested=0
    for removed in sorted(chosen):
        for added in sorted(ids-chosen):
            candidate=sorted((chosen-{removed})|{added});tested+=1
            err,total=constraints(task,candidate)
            if err or total['value']<=old['value']:continue
            witness={'selected':candidate,**total,'value_gain':total['value']-old['value'],
                     'cost_delta':total['cost']-old['cost'],'time_delta':total['time']-old['time']}
            if best is None or witness['value']>best['value']:best=witness
    digest=hashlib.sha256(json.dumps(task,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    result={'task_sha256':digest,'checked_neighbors':tested,'global_optimality':'UNKNOWN',
            'status':'BETTER_FEASIBLE_WITNESS' if best else 'NO_ONE_SWAP_IMPROVEMENT_FOUND'}
    if best:
        result.update(original={'selected':sorted(selected),**old},witness=best,
                      certified='The original candidate is not globally optimal for this fixed input.')
    return result

class Tests(unittest.TestCase):
    def task(self):
        return {'choose':1,'items':[{'id':'A','time':3,'cost':5,'value':7},{'id':'B','time':2,'cost':4,'value':9}],
                'limits':{'time':5,'cost':6},'incompatible':[],'requires':[]}
    def test_improvement(self):self.assertEqual(check(self.task(),['A'])['witness']['selected'],['B'])
    def test_does_not_claim_optimal(self):self.assertEqual(check(self.task(),['B'])['global_optimality'],'UNKNOWN')
    def test_unknown_ids(self):self.assertEqual(check(self.task(),['Z'])['status'],'NOT_APPLICABLE')
    def test_infeasible_witness_excluded(self):
        t=self.task();t['items'][1]['cost']=10
        self.assertEqual(check(t,['A'])['status'],'NO_ONE_SWAP_IMPROVEMENT_FOUND')
    def test_requires_respected(self):
        t=self.task();t['requires']=[['B','A']]
        self.assertEqual(check(t,['A'])['status'],'NO_ONE_SWAP_IMPROVEMENT_FOUND')
    def test_no_mutation(self):
        t=self.task();s=['A'];before=json.dumps([t,s],sort_keys=True);check(t,s)
        self.assertEqual(json.dumps([t,s],sort_keys=True),before)
    def test_two_swap_trap(self):
        t={'choose':2,'items':[{'id':x,'time':1,'cost':1,'value':v} for x,v in [('A',1),('B',1),('C',3),('D',3)]],
           'limits':{'time':2,'cost':2},'requires':[['C','D'],['D','C']],'incompatible':[]}
        r=check(t,['A','B'])
        self.assertEqual(r['status'],'NO_ONE_SWAP_IMPROVEMENT_FOUND')
        self.assertEqual(r['global_optimality'],'UNKNOWN')

if __name__=='__main__':unittest.main()
