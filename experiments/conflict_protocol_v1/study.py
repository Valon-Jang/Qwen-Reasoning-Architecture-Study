#!/usr/bin/env python3
"""Same-source exploratory follow-up, not a fresh confirmation.
Zero model calls on unambiguous records; model chooses only conflicting record ID.
"""
import copy, importlib.util, json, pathlib, re, shutil, subprocess, sys, tempfile, time
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments'/'posthoc'))
import conflict_only_candidate as compiler
s=compiler.study;transport=s.transport;instrument=s.instrument
ID='Q35_2B_CONFLICT_ONLY_FOLLOWUP_V1'
BASE='Select the currently effective source record. Return only its reference ID.'

def request(task,key,options):
    return [{'role':'system','content':BASE},{'role':'user','content':task['source']+'\n\nFor compilation only: which record is currently effective for '+key+'? Choose exactly one of: '+', '.join(options)+'. Return only that exact reference ID, without JSON or explanation.'}]

def main():
    out=pathlib.Path('results/conflict_protocol_v1_live');out.mkdir(parents=True,exist_ok=True)
    if (out/'events.jsonl').exists():raise RuntimeError('REFUSE_OVERWRITE')
    tasks=s.cases();records=[];health=[];errors=[];calls=0;proc=None;identity={};start=time.monotonic()
    reg={'id':ID,'prior_run':34758271938,'same_development_sources_reused':True,'fresh_confirmation':False,
         'source_cases_sha256':s.digest(tasks),'script_sha256':transport.file_sha(__file__),
         'compiler_sha256':transport.file_sha(compiler.__file__),'repeats':2,'maximum_model_calls':10,
         'source_outcomes':16,'zero_call_sources_per_repeat':5,'model_resolved_sources_per_repeat':3,
         'change':'retain every unambiguous typed record; enum choice only in conflicting scalar/item group',
         'no_hidden_gold_in_choices':True,'budget_seconds':600,'promotion':'NOT_PROMOTED'}
    s.store(out/'registration.json',reg);s.store(out/'cases.json',tasks)
    def event(x):
        with (out/'events.jsonl').open('a',encoding='utf-8') as f:f.write(s.canonical(x)+'\n');f.flush()
    def result():
        responses=[h['response'] for h in health]+[r['response'] for r in records if r['response'] is not None]
        return {'experiment':ID,'status':'COMPLETE' if len(records)==16 and not errors else 'INCOMPLETE',
          'prior_run':34758271938,'scope':'same constructed source set, post-result exploratory follow-up; not a held-out replication',
          'model':identity,'outcomes':len(records),'source_fidelity_pass':sum(r['source_fidelity'] is True for r in records),
          'semantic_pass':sum(r['semantic_pass'] is True for r in records),'case_pass':sum(r['case_pass'] for r in records),
          'format_pass':sum(r['format_pass'] for r in records),'zero_call_outcomes':sum(r['response'] is None for r in records),
          'model_resolved_outcomes':sum(r['response'] is not None for r in records),
          'actual_model_calls_started':calls,'actual_model_calls_completed':len(responses),
          'known_physical_tokens':sum((r.get('usage') or {}).get('total_tokens',0) for r in responses),
          'unknown_usage':sum(not r.get('usage') for r in responses),'records':records,'health':health,'errors':errors,
          'elapsed_ms':round((time.monotonic()-start)*1000,2),'user_manual_test_steps':0,'promotion':'NOT_PROMOTED'}
    def save():s.store(out/'summary.json',result())
    with tempfile.TemporaryDirectory(prefix='qwen-conflict-') as td:
        work=pathlib.Path(td)
        try:
            proc,identity=instrument.provision(work,out)
            for i,(name,text,expected) in enumerate(instrument.HEALTH):
                msg=[{'role':'system','content':transport.BASE_SYSTEM},{'role':'user','content':text}];calls+=1
                event({'event':'start','kind':'canary','id':name,'request':msg,'seed':9300+i})
                rr=transport.infer(msg,9300+i);obj,fmt=s.parse(rr['text']);v=obj.get('answer') if isinstance(obj,dict) else None
                h={'id':name,'response':rr,'pass':type(v)==type(expected) and v==expected and fmt and rr['finish_reason']=='stop'}
                health.append(h);event({'event':'complete','kind':'canary','record':h});save()
            if not all(h['pass'] for h in health):raise RuntimeError('CANARY_FAILED')
            for rep in range(2):
                for idx,t in enumerate(tasks):
                    if time.monotonic()-start>600:raise TimeoutError('STUDY_BUDGET')
                    begin=time.monotonic();plan=compiler.build_plan(t['source']);choices={};rr=None;fmt=True;error=None
                    if plan['conflicts']:
                        assert len(plan['conflicts'])==1
                        key,options=next(iter(plan['conflicts'].items()));msg=request(t,key,options)
                        seed=42000+100*rep+idx;calls+=1
                        event({'event':'start','kind':'study','case_id':t['id'],'repeat':rep+1,'request':msg,'seed':seed})
                        rr=transport.infer(msg,seed);chosen=rr['text'].strip()
                        fmt=chosen in options and rr['finish_reason']=='stop'
                        choices[key]=chosen
                    try:compiled=compiler.apply_choices(plan,choices)
                    except ValueError as exc:compiled=None;error=str(exc)
                    elapsed=round((time.monotonic()-begin)*1000,4)
                    answer=compiled['answer'] if compiled else None
                    # The following labels are offline evaluation only, not operational gates.
                    fidelity=compiled['spec']==s.normalize(t['gold']) if compiled else None
                    semantic=s.score_answer(t['gold'],answer)
                    row={'case_id':t['id'],'repeat':rep+1,'choices':choices,'conflicts':plan['conflicts'],
                         'response':rr,'compiled':compiled,'semantic_pass':semantic,'source_fidelity':fidelity,
                         'format_pass':fmt,'case_pass':semantic is True and fmt,'error':error,'elapsed_ms':elapsed}
                    records.append(row);event({'event':'complete','kind':'study','record':row});save()
                    print('CONFLICT_RESULT '+s.canonical(row),flush=True)
        except Exception as exc:errors.append({'class':type(exc).__name__,'detail':str(exc)[:500]});save()
        finally:
            if proc:
                proc.terminate()
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
            if (work/'server.log').exists():shutil.copyfile(work/'server.log',out/'server.log')
    save();print('FINAL_CONFLICT '+s.canonical(result()),flush=True)
    if errors:raise SystemExit(2)
if __name__=='__main__':main()
