#!/usr/bin/env python3
"""Follow-up to all-zero pilot: calibration and matched input-representation test.
No prompt tuning on hidden labels. Same 12 development tasks, NOT held-out.
"""
import json, pathlib, shutil, tempfile, time, sys, unittest
import run as pilot
import launch_uq8 as instrument
EXPERIMENT='Q35_08B_CALIBRATION_REPRESENTATION_V1'


def concrete(t):
    if t['language']=='ko':
        text=f'정확히 {t["choose"]}개의 서로 다른 항목을 선택하라. 시간 합계는 {t["limits"]["time"]} 이하, 비용 합계는 {t["limits"]["cost"]} 이하여야 한다. 조건을 만족하는 조합 중 가치 합계가 최대인 것을 선택하라.'
        columns='ID | 시간 | 비용 | 가치'
        notes=[f'{a}와 {b}는 함께 선택할 수 없다.' for a,b in t['incompatible']]+[f'{a}를 선택하면 {b}도 반드시 선택해야 한다.' for a,b in t['requires']]
        end='selected는 선택한 ID 배열이다. time, cost, value는 선택한 항목들의 시간, 비용, 가치 합계다. 최종 JSON 객체만 출력하라.'
    else:
        text=f'Select exactly {t["choose"]} distinct items. Total time must be at most {t["limits"]["time"]} and total cost at most {t["limits"]["cost"]}. Maximize total value over all selections satisfying these conditions.'
        columns='ID | time | cost | value'
        notes=[f'Do not select {a} and {b} together.' for a,b in t['incompatible']]+[f'Selecting {a} also requires selecting {b}.' for a,b in t['requires']]
        end='selected is the selected ID array. time, cost, value are the sums for those IDs. Return only the final JSON object.'
    table='\n'.join(f'{x["id"]} | {x["time"]} | {x["cost"]} | {x["value"]}' for x in t['items'])
    return text+'\n'+columns+'\n'+table+'\n'+'\n'.join(notes)+'\n'+end+'\nSchema: {"selected":["A","B"],"time":0,"cost":0,"value":0}'

HEALTH=[
('echo_en','Return only this exact JSON object: {"answer":"CHECK_7429"}', 'CHECK_7429'),
('add_en','What is 4 + 7? Return only JSON with the integer result as answer, such as {"answer":0}.',11),
('add_ko','4 더하기 7의 값을 answer에 넣어 JSON 객체만 출력하라. 형식: {"answer":0}',11),
('max_two','A has value 3. B has value 9. Which ID has the greater value? Return only {"answer":"A"} or {"answer":"B"}.','B')]


def execute(out):
    out.mkdir(parents=True,exist_ok=True);pilot.EXPERIMENT=EXPERIMENT
    tasks=pilot.cases(); records=[];health=[];calls=0;errors=[];proc=None;identity={};start=time.monotonic()
    spec={'id':EXPERIMENT,'reason':'previous pilot 0/12 all arms; check instrument and avoid floor-effect promotion',
          'cases_sha256':pilot.sha(pilot.dumps(tasks).encode()),'arms':['RAW_JSON_BASELINE','CONCRETE_TEXT'],'repeats':1,
          'development_set_reused':True,'change':'same facts/constraints/objective/output schema; bind scalar values explicitly and render items as a table',
          'unknown_native_compute_claim':False,'maximum_calls':28,'user_manual_test_steps':0}
    pilot.write(out/'calibration_registration.json',spec);pilot.write(out/'cases.json',tasks)
    def checkpoint():
        sums={}
        for arm in spec['arms']:
            rs=[r for r in records if r['arm']==arm]
            sums[arm]={'case_runs':len(rs),'semantic_pass':sum(r['score']['semantic_pass'] is True for r in rs),
              'unscorable':sum(r['score']['semantic_pass'] is None for r in rs),'format_pass':sum(r['score']['format_pass'] for r in rs),
              'case_pass':sum(r['score']['case_pass'] for r in rs),'model_calls':len(rs),
              'known_tokens':sum((r['response'].get('usage') or {}).get('total_tokens',0) for r in rs),
              'usage_unknown':sum(not r['response'].get('usage') for r in rs),
              'median_ms':pilot.statistics.median(r['response']['elapsed_ms'] for r in rs) if rs else None}
        result={'experiment':EXPERIMENT,'model':identity,'health':health,'arms':sums,'actual_model_calls_started':calls,
                'status':'COMPLETE' if len(records)==24 and len(health)==4 and not errors else 'INCOMPLETE',
                'errors':errors,'research_elapsed_ms':round((time.monotonic()-start)*1000,2),'user_manual_test_steps':0,
                'promotion':'NOT_PROMOTED','interpretation':'Development calibration only; no large-model or Max-like performance claim.'}
        pilot.write(out/'calibration_summary.json',result)
        return result
    with tempfile.TemporaryDirectory(prefix='qwen-calibration-') as td:
        work=pathlib.Path(td)
        try:
            proc,identity=instrument.provision(work,out)
            identity['calibration_script_sha256']=pilot.file_sha(__file__)
            for idx,(name,text,expected) in enumerate(HEALTH):
                calls+=1;rr=pilot.infer([{'role':'system','content':pilot.BASE_SYSTEM},{'role':'user','content':text}],7300+idx)
                obj,fmt=pilot.parse(rr['text']); answer=obj.get('answer') if isinstance(obj,dict) else None
                entry={'id':name,'response':rr,'semantic_pass':type(answer)==type(expected) and answer==expected,'format_pass':fmt,'expected':expected}
                health.append(entry); print('HEALTH_RESULT '+pilot.dumps(entry),flush=True);checkpoint()
            for idx,t in enumerate(tasks):
                order=spec['arms'] if idx%2==0 else list(reversed(spec['arms']))
                for arm in order:
                    if time.monotonic()-start>1050: raise TimeoutError('CALIBRATION_BUDGET')
                    text=pilot.prompt(t) if arm=='RAW_JSON_BASELINE' else concrete(t)
                    calls+=1;rr=pilot.infer([{'role':'system','content':pilot.BASE_SYSTEM},{'role':'user','content':text}],20260913+idx)
                    score=pilot.score(t,rr['text']) if rr['finish_reason']=='stop' else {'semantic_pass':None,'format_pass':False,'case_pass':False,'unscorable':True,'silent_suboptimal':False}
                    rec={'case_id':t['id'],'language':t['language'],'arm':arm,'prompt':text,'response':rr,'score':score}
                    records.append(rec)
                    with open(out/'calibration_results.jsonl','a') as f:f.write(pilot.dumps(rec)+'\n')
                    print('CALIBRATION_RESULT '+pilot.dumps(rec),flush=True);checkpoint()
        except Exception as e:
            errors.append({'class':type(e).__name__,'detail':str(e)[:600]})
        finally:
            if proc:
                proc.terminate()
                try:proc.wait(timeout=10)
                except pilot.subprocess.TimeoutExpired:proc.kill();proc.wait()
            if (work/'server.log').exists():shutil.copyfile(work/'server.log',out/'server.log')
    print('FINAL_CALIBRATION '+pilot.dumps(checkpoint()),flush=True)
    if errors: raise SystemExit(2)

class RenderTests(unittest.TestCase):
    def test_all_item_values_preserved(self):
        for t in pilot.cases():
            s=concrete(t)
            for x in t['items']:self.assertIn(f'{x["id"]} | {x["time"]} | {x["cost"]} | {x["value"]}',s)
    def test_no_oracle_dependency(self):
        old=pilot.oracle
        tasks=pilot.cases()
        def blocked(_):raise AssertionError('oracle accessed')
        pilot.oracle=blocked
        try:
            for t in tasks:self.assertTrue(concrete(t))
        finally:pilot.oracle=old
    def test_constraint_text_presence(self):
        for t in pilot.cases():
            text=concrete(t)
            for a,b in t['requires']+t['incompatible']:self.assertIn(a,text);self.assertIn(b,text)
            self.assertIn(str(t['choose']),text)
            for n in t['limits'].values():self.assertIn(str(n),text)

if __name__=='__main__':
    if '--self-test' in sys.argv:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RenderTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    execute(pathlib.Path('results/autolab_v1_live'))
