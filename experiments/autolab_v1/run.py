#!/usr/bin/env python3
"""Bounded real-Qwen development pilot. Only synthetic inputs; no user credentials.
Two recovery policies branch from the SAME initial sample. Operational validator
uses task inputs only and intentionally cannot judge optimality. Hidden scoring
uses an independent exhaustive oracle, never passed to generation or feedback.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, os, pathlib, random, re, shutil
import socket, statistics, subprocess, sys, tarfile, tempfile, time, unittest
import urllib.request

EXPERIMENT = 'Q35_SMALL_REAL_FEEDBACK_PILOT_V1'
MODEL_REPO = 'ggerganov/Qwen3.5-0.8B-GGUF'
MODEL_SOURCE = 'Qwen/Qwen3.5-0.8B'
LLAMA_TAG = 'b10344'
COUNT = 12
BASE_SYSTEM = 'Solve the user task. Return only the requested final JSON object.'
RECHECK = 'Re-evaluate your answer against the original task. Return only a corrected final JSON object; keep the requested schema.'
TIMEOUT = 100
JOB_BUDGET = 1050


def dumps(x): return json.dumps(x, ensure_ascii=False, sort_keys=True)
def sha(x): return hashlib.sha256(x).hexdigest()
def file_sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def write(p, x):
    p=pathlib.Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp'); t.write_text(dumps(x)+'\n',encoding='utf-8'); os.replace(t,p)
def read_url(url, timeout=60):
    req=urllib.request.Request(url,headers={'User-Agent':'Qwen-Reasoning-Architecture-Study/Autolab-v1'})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read()
def api(url): return json.loads(read_url(url))
def download(url,p,expected=None,limit=1200000000):
    req=urllib.request.Request(url,headers={'User-Agent':'Qwen-Reasoning-Architecture-Study/Autolab-v1'})
    n=0
    with urllib.request.urlopen(req,timeout=90) as r,open(p,'wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            n+=len(b)
            if n>limit: raise RuntimeError('DOWNLOAD_SIZE_LIMIT')
            f.write(b)
    actual=file_sha(p)
    if expected and actual!=expected: raise RuntimeError('DOWNLOAD_HASH_MISMATCH')
    return {'sha256':actual,'bytes':n,'publisher_hash_verified':bool(expected)}


def constraints(t, selected):
    # Shared predicate over explicit task data, not hidden gold.
    ss=set(selected); by={x['id']:x for x in t['items']}
    errors=[]
    if len(selected)!=t['choose'] or len(ss)!=len(selected): errors.append('wrong selection count or duplicate IDs')
    if not ss<=by.keys(): return errors+['unknown ID'], None
    totals={k:sum(by[i][k] for i in ss) for k in ('time','cost','value')}
    for k in ('time','cost'):
        if totals[k]>t['limits'][k]: errors.append(f'{k} sum {totals[k]} exceeds limit {t["limits"][k]}')
    for a,b in t['incompatible']:
        if a in ss and b in ss: errors.append(f'incompatible pair {a},{b}')
    for a,b in t['requires']:
        if a in ss and b not in ss: errors.append(f'{a} requires {b}')
    return errors,totals


def oracle(t):
    # Independent exhaustive hidden scorer. Do not call this from validator.
    candidates=[]
    for group in itertools.combinations(t['items'],t['choose']):
        ids={x['id'] for x in group}
        if any(a in ids and b in ids for a,b in t['incompatible']): continue
        if any(a in ids and b not in ids for a,b in t['requires']): continue
        cost=sum(x['cost'] for x in group); tm=sum(x['time'] for x in group)
        if cost>t['limits']['cost'] or tm>t['limits']['time']: continue
        candidates.append((sum(x['value'] for x in group),tuple(sorted(ids))))
    if not candidates: return None,[]
    best=max(v for v,s in candidates)
    return best,[list(s) for v,s in candidates if v==best]


def cases():
    rng=random.Random(2026091308); out=[]
    while len(out)<COUNT:
        i=len(out); n=7 if i%2 else 6; choose=3 if i%3 else 2
        items=[dict(id=chr(65+j),time=rng.randint(2,10),cost=rng.randint(3,14),value=rng.randint(5,24)) for j in range(n)]
        task={'id':f'P{i+1:02}','language':'ko' if i%2 else 'en','choose':choose,'items':items,
              'limits':{'time':rng.randint(11,21),'cost':rng.randint(15,28)},
              'incompatible':[['A','B']] if i%3==1 else [],
              'requires':[['C','D']] if i%3==2 else []}
        best,sets=oracle(task)
        if best is not None and len(sets)==1: out.append(task)
    return out


def prompt(t):
    if t['language']=='ko':
        txt='각 항목은 한 번만 선택할 수 있다. 정확히 choose개를 선택하라. time 합계와 cost 합계는 각각 limits 이하여야 한다. incompatible 쌍은 함께 선택할 수 없다. requires의 [X,Y]는 X를 선택하면 Y도 반드시 선택한다는 뜻이다. 모든 조건을 만족하는 조합 중 value 합계가 최대인 조합을 구하라. 최종 JSON만 출력하라. selected는 ID 배열이며 time, cost, value는 선택한 항목의 정확한 합계이다.'
    else:
        txt='Select exactly choose distinct items. The sums of time and cost must each be at most their limits. An incompatible pair cannot be selected together. A requires pair [X,Y] means selecting X requires selecting Y. Maximize the sum of value among feasible combinations. Return only final JSON: selected is an array of IDs and time, cost, value are the exact sums for those IDs.'
    data={k:t[k] for k in ('choose','items','limits','incompatible','requires')}
    return txt+'\nSchema: {"selected":["A","B"],"time":0,"cost":0,"value":0}\nData:\n'+dumps(data)


def parse(s):
    try:
        obj=json.loads(s.strip()); return obj,True
    except (ValueError,TypeError): pass
    # Recover one top-level JSON object without silently choosing among many.
    decoder=json.JSONDecoder(); objs=[]; pos=0
    while pos<len(s):
        idx=s.find('{',pos)
        if idx<0: break
        try:
            o,end=decoder.raw_decode(s[idx:]); objs.append(o); pos=idx+end
        except ValueError: pos=idx+1
    return (objs[0],False) if len(objs)==1 else (None,False)


def validate(t, text):
    obj,strict=parse(text); errors=[]
    if not isinstance(obj,dict): return ['no unique final JSON object'],obj,False
    keys={'selected','time','cost','value'}
    if set(obj)!=keys: errors.append('schema requires exactly selected,time,cost,value')
    sel=obj.get('selected')
    if not isinstance(sel,list) or any(not isinstance(x,str) for x in sel):
        return errors+['selected must be an ID array'],obj,False
    e,totals=constraints(t,sel); errors+=e
    for k in ('time','cost','value'):
        x=obj.get(k)
        if type(x) is not int: errors.append(k+' must be an integer')
        elif totals is not None and x!=totals[k]: errors.append(f'{k} reported {x}; recomputed from your selected IDs: {totals[k]}')
    if not strict: errors.append('extra text outside JSON')
    fmt=strict and set(obj)==keys and all(type(obj.get(k)) is int for k in ('time','cost','value'))
    return errors,obj,fmt


def score(t,text):
    errors,obj,fmt=validate(t,text); best,winners=oracle(t)
    if not isinstance(obj,dict) or not isinstance(obj.get('selected'),list) or any(not isinstance(x,str) for x in obj['selected']):
        return {'semantic_pass':None,'format_pass':False,'case_pass':False,'unscorable':True,'silent_suboptimal':False}
    e,totals=constraints(t,obj['selected'])
    sums_ok=totals is not None and all(type(obj.get(k)) is int and obj[k]==totals[k] for k in ('time','cost','value'))
    sem=not e and sums_ok and totals['value']==best
    return {'semantic_pass':bool(sem),'format_pass':bool(fmt),'case_pass':bool(sem and fmt),
            'unscorable':False,'silent_suboptimal':bool(not errors and not sem)}


def provision(work,out):
    release=api(f'https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/{LLAMA_TAG}')
    assets=[a for a in release['assets'] if a['name']==f'llama-{LLAMA_TAG}-bin-ubuntu-x64.tar.gz']
    if len(assets)!=1: raise RuntimeError('NO_EXACT_CPU_ASSET')
    a=assets[0]; expected=a.get('digest') or ''
    rt=download(a['browser_download_url'],work/'runtime.tar.gz',expected.removeprefix('sha256:') if expected.startswith('sha256:') else None,500000000)
    with tarfile.open(work/'runtime.tar.gz') as tar: tar.extractall(work/'runtime',filter='data')
    bins=list((work/'runtime').rglob('llama-server'))
    if len(bins)!=1: raise RuntimeError('RUNTIME_BINARY_AMBIGUOUS')
    binary=bins[0]; binary.chmod(binary.stat().st_mode|0o111)
    meta=api('https://huggingface.co/api/models/'+MODEL_REPO+'?blobs=true')
    files=[f for f in meta['siblings'] if f['rfilename'].endswith('Q8_0.gguf') and 'mmproj' not in f['rfilename'].lower()]
    if len(files)!=1: raise RuntimeError('NO_EXACT_Q8_MODEL')
    f=files[0]; revision=meta['sha']; model=work/'model.gguf'
    digest=f.get('lfs',{}).get('sha256')
    if not digest: raise RuntimeError('MODEL_PUBLISHER_HASH_MISSING')
    w=download(f'https://huggingface.co/{MODEL_REPO}/resolve/{revision}/{f["rfilename"]}',model,digest)
    env=os.environ.copy(); env['LD_LIBRARY_PATH']=str(binary.parent)+':'+env.get('LD_LIBRARY_PATH','')
    version=subprocess.check_output([str(binary),'--version'],env=env,stderr=subprocess.STDOUT,text=True,timeout=20)
    helptext=subprocess.check_output([str(binary),'--help'],env=env,stderr=subprocess.STDOUT,text=True,timeout=20)
    for flag in ('--jinja','--chat-template-kwargs'):
        if flag not in helptext: raise RuntimeError('RUNTIME_FLAG_UNSUPPORTED:'+flag)
    identity={'base_model':MODEL_SOURCE,'model_repo':MODEL_REPO,'model_revision':revision,'model_file':f['rfilename'],
              'weights':w,'runtime_release':LLAMA_TAG,'runtime_asset':a['name'],'runtime_asset_hash':rt,
              'runtime_version':version,'binary_sha256':file_sha(binary),'inference_device':'CPU','threads':4,
              'thinking':False,'temperature':0.6,'top_p':0.95,'top_k':20,'context_tokens':8192,
              'client_max_tokens':None,'server_n_predict':-1,'request_timeout_seconds':TIMEOUT,
              'script_sha256':file_sha(__file__),'git_commit':os.getenv('GITHUB_SHA'),
              'github_run_id':os.getenv('GITHUB_RUN_ID'),'target_reference':'NOT_MEASURED'}
    write(out/'identity.json',identity); print('MODEL_IDENTITY '+dumps(identity),flush=True)
    log=open(work/'server.log','w')
    cmd=[str(binary),'-m',str(model),'--host','127.0.0.1','--port','8080','-c','8192','-t','4','-np','1','-ngl','0','-n','-1','--jinja','--chat-template-kwargs','{"enable_thinking":false}']
    proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
    for _ in range(120):
        if proc.poll() is not None:
            print((work/'server.log').read_text()[-6000:]); raise RuntimeError('SERVER_EXIT')
        try:
            health=api('http://127.0.0.1:8080/health')
            if health.get('status')=='ok': return proc,identity
        except Exception: pass
        time.sleep(1)
    proc.terminate(); raise RuntimeError('SERVER_START_TIMEOUT')


def infer(messages,seed):
    payload={'model':MODEL_SOURCE,'messages':messages,'temperature':0.6,'top_p':0.95,'top_k':20,'seed':seed,
             'stream':False,'cache_prompt':False,'chat_template_kwargs':{'enable_thinking':False}}
    assert 'max_tokens' not in payload
    start=time.monotonic()
    req=urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions',data=dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=TIMEOUT) as r: response=json.load(r)
    choice=response['choices'][0]; msg=choice['message']; text=msg.get('content') or ''
    return {'text':text,'usage':response.get('usage'), 'elapsed_ms':round((time.monotonic()-start)*1000,2),
            'finish_reason':choice.get('finish_reason'),'returned_model':response.get('model'),
            'seed':seed,'request_sha256':sha(dumps(payload).encode()),'reasoning_field_returned':bool(msg.get('reasoning_content'))}


def summarize(records, identity, calls,complete):
    arms={}
    for arm in ('BARE','SELF_REVIEW','VERIFIED_REPAIR'):
        rr=[r for r in records if r['arm']==arm]
        scored=[r for r in rr if r.get('score')]
        passed=sum(r['score']['semantic_pass'] is True for r in scored)
        unknown=sum(r['score']['semantic_pass'] is None for r in scored)
        arms[arm]={'case_runs':len(rr),'semantic_pass':passed,'format_pass':sum(r['score']['format_pass'] for r in scored),
                   'case_pass':sum(r['score']['case_pass'] for r in scored),'unscorable':unknown,
                   'silent_suboptimal':sum(r['score']['silent_suboptimal'] for r in scored),
                   'semantic_bounds_over_completed':[passed/len(rr),(passed+unknown)/len(rr)] if rr else None,
                   'logical_model_calls':sum(r['logical_calls'] for r in rr),
                   'known_total_tokens':sum(r['logical_tokens'] for r in rr if r['logical_tokens'] is not None),
                   'unknown_usage_records':sum(r['logical_tokens'] is None for r in rr),
                   'median_case_ms':statistics.median([r['logical_ms'] for r in rr]) if rr else None}
    return {'experiment':EXPERIMENT,'status':'DEVELOPMENT_PILOT_COMPLETE' if complete else 'INCOMPLETE',
            'model':identity,'actual_generation_calls':calls,'arms':arms,
            'shared_prefix_design':True,'input_distribution':'12 synthetic selection optimization cases, 6 English / 6 Korean; one seeded sample each',
            'claim':'Mechanism screening only; no target-deployment, 3.8-Max, or statistical superiority claim.',
            'promotion':'NOT_PROMOTED','user_manual_test_steps':0}


def run(out):
    out.mkdir(parents=True,exist_ok=True); tasks=cases()
    write(out/'cases.json',tasks)
    protocol={'id':EXPERIMENT,'cases_sha256':sha(dumps(tasks).encode()),'arms':['BARE','SELF_REVIEW','VERIFIED_REPAIR'],
              'initial_sample_shared':True,'repair_trigger':'input-only schema/selection/feasibility/sum validator; no optimality oracle',
              'max_repair_calls_per_policy':1,'repeats':1,'split':'development_screening',
              'no_silent_token_cap':True,'per_request_timeout_seconds':TIMEOUT,'experiment_budget_seconds':JOB_BUDGET}
    write(out/'preregistration.json',protocol)
    records=[]; calls=0; proc=None; identity={}; errors=[]; start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='qwen-autolab-') as td:
        work=pathlib.Path(td)
        try:
            proc,identity=provision(work,out)
            for idx,t in enumerate(tasks):
                if time.monotonic()-start>JOB_BUDGET: raise TimeoutError('EXPERIMENT_BUDGET_EXHAUSTED')
                messages=[{'role':'system','content':BASE_SYSTEM},{'role':'user','content':prompt(t)}]
                calls+=1; first=infer(messages,20260913+idx)
                feedback,_,_=validate(t,first['text'])
                initial_usage=(first.get('usage') or {}).get('total_tokens')
                def save(arm, sample, extra=False):
                    u=(sample.get('usage') or {}).get('total_tokens')
                    cost=initial_usage if not extra else (initial_usage+u if initial_usage is not None and u is not None else None)
                    result={'case_id':t['id'],'language':t['language'],'arm':arm,'initial':first,'final':sample,
                            'feedback':feedback,'triggered':bool(feedback),'logical_calls':1+int(extra),
                            'logical_tokens':cost,'logical_ms':first['elapsed_ms']+(sample['elapsed_ms'] if extra else 0),
                            'score':score(t,sample['text']) if sample['finish_reason']=='stop' else {'semantic_pass':None,'format_pass':False,'case_pass':False,'unscorable':True,'silent_suboptimal':False}}
                    records.append(result)
                    with open(out/'results.jsonl','a',encoding='utf-8') as f: f.write(dumps(result)+'\n')
                    write(out/'summary.json',summarize(records,identity,calls,False))
                    print('CASE_RESULT '+dumps(result),flush=True)
                save('BARE',first)
                order=['SELF_REVIEW','VERIFIED_REPAIR'] if idx%2==0 else ['VERIFIED_REPAIR','SELF_REVIEW']
                for arm in order:
                    if not feedback:
                        save(arm,first); continue
                    if first['finish_reason']!='stop': raise RuntimeError('INITIAL_NOT_COMPLETED')
                    if time.monotonic()-start>JOB_BUDGET: raise TimeoutError('EXPERIMENT_BUDGET_EXHAUSTED')
                    instruction=RECHECK
                    if arm=='VERIFIED_REPAIR': instruction+='\nInput-based validator findings (not a solution):\n'+dumps(feedback)
                    follow=messages+[{'role':'assistant','content':first['text']},{'role':'user','content':instruction}]
                    calls+=1; corrected=infer(follow,20261013+idx)
                    save(arm,corrected,True)
        except Exception as e:
            errors.append({'class':type(e).__name__,'detail':str(e)[:600],'actual_calls_started':calls})
            print('EXECUTION_ERROR '+dumps(errors[-1]),flush=True)
        finally:
            if proc:
                proc.terminate()
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
            if (work/'server.log').exists(): shutil.copyfile(work/'server.log',out/'server.log')
    summary=summarize(records,identity,calls,len(records)==COUNT*3 and not errors)
    summary.update(errors=errors,research_elapsed_ms=round((time.monotonic()-start)*1000,2))
    write(out/'summary.json',summary); print('FINAL_SUMMARY '+dumps(summary),flush=True)
    if errors: raise SystemExit(2)


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.t=cases()[0]; cls.best,cls.winners=oracle(cls.t)
    def good(self):
        _,tot=constraints(self.t,self.winners[0]); return {'selected':list(self.winners[0]),**tot}
    def test_fixture_copy_isolation(self):
        x=self.good(); x['selected'][0]='ZZ'; self.assertNotIn('ZZ',self.winners[0])
    def test_case_count(self): self.assertEqual(len(cases()),12)
    def test_case_balance(self): self.assertEqual(sum(t['language']=='ko' for t in cases()),6)
    def test_unique_optima(self): self.assertTrue(all(len(oracle(t)[1])==1 for t in cases()))
    def test_fixture_determinism(self): self.assertEqual(cases(),cases())
    def test_correct_answer(self): self.assertTrue(score(self.t,dumps(self.good()))['case_pass'])
    def test_no_feedback_for_correct(self): self.assertEqual(validate(self.t,dumps(self.good()))[0],[])
    def test_wrong_sum(self):
        x=self.good(); x['cost']+=1; self.assertTrue(validate(self.t,dumps(x))[0]); self.assertFalse(score(self.t,dumps(x))['semantic_pass'])
    def test_unknown_id(self):
        x=self.good(); x['selected'][0]='ZZ'; self.assertTrue(validate(self.t,dumps(x))[0])
    def test_duplicate(self):
        x=self.good(); x['selected']=[x['selected'][0]]*self.t['choose']; self.assertTrue(validate(self.t,dumps(x))[0])
    def test_extra_text(self):
        x='Answer: '+dumps(self.good()); s=score(self.t,x); self.assertTrue(s['semantic_pass']); self.assertFalse(s['format_pass'])
    def test_two_objects(self): self.assertIsNone(parse('{} {}')[0])
    def test_bool_not_int(self):
        x=self.good(); x['cost']=True; self.assertFalse(score(self.t,dumps(x))['semantic_pass'])
    def test_missing_field(self):
        x=self.good(); del x['time']; self.assertFalse(score(self.t,dumps(x))['case_pass'])
    def test_no_gold_in_prompt(self): self.assertNotIn('winners',prompt(self.t))
    def test_incompatibility(self):
        t=cases()[1]; self.assertTrue(constraints(t,['A','B','E'])[0])
    def test_requires(self):
        t=cases()[2]; self.assertTrue(any('requires' in s for s in constraints(t,['A','C','E'])[0]))
    def test_unscorable(self): self.assertIsNone(score(self.t,'I do not know')['semantic_pass'])
    def test_independent_validator_blind_spot(self):
        found=False
        for t in cases():
            best,_=oracle(t)
            for items in itertools.combinations(t['items'],t['choose']):
                selected=[x['id'] for x in items]; e,tot=constraints(t,selected)
                if not e and tot['value']<best:
                    txt=dumps({'selected':selected,**tot}); self.assertEqual(validate(t,txt)[0],[])
                    self.assertTrue(score(t,txt)['silent_suboptimal']); found=True; break
            if found: break
        self.assertTrue(found)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--self-test',action='store_true'); ap.add_argument('--out',default='results/autolab_v1_live')
    args=ap.parse_args()
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests); r=unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if r.wasSuccessful() else 1)
    run(pathlib.Path(args.out))
