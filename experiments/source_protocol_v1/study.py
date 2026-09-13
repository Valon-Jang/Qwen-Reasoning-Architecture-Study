#!/usr/bin/env python3
"""Fresh source-fidelity pilot: direct answer vs two SAME-SOLVER interfaces.
Only synthetic text. Source references select visible rows, never hidden gold.
This is an engineered-task system study, not an intrinsic intelligence claim.
"""
from __future__ import annotations
import argparse, copy, hashlib, itertools, json, math, os, pathlib, re, shutil
import statistics, subprocess, sys, tempfile, time, unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments' / 'autolab_v1'))
import run as transport
import scale_probe as instrument

EXPERIMENT = 'Q35_2B_SOURCE_FIDELITY_SAME_SOLVER_V1'
ARMS = ['DIRECT', 'VALUE_TOOL', 'REF_TOOL']
REPEATS = 2
BUDGET_SECONDS = 1400
BASE = 'Use only the supplied source. Apply its final instructions. Return one JSON object, without commentary.'
FIELDS = {'items','pick','time_limit','cost_limit','excluded','requires','incompatible'}
ANSWER_FIELDS = {'selected','time','cost','value'}

def canonical(x): return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',',':'))
def digest(x): return hashlib.sha256(canonical(x).encode()).hexdigest()
def store(path,x): transport.write(path,x)

def spec(rows,k,tm,cost,excluded=(),requires=(),incompatible=()):
    return {'items':[dict(zip(['id','time','cost','value'],r)) for r in rows], 'pick':k,
            'time_limit':tm,'cost_limit':cost,'excluded':list(excluded),
            'requires':[list(p) for p in requires], 'incompatible':[list(p) for p in incompatible]}

def cases():
    definitions = [
      ('S01','en','clean_single',spec([('A',5,7,11),('B',2,3,9),('C',4,6,13)],1,9,8)),
      ('S02','ko','clean_pair',spec([('A',2,3,8),('B',3,4,10),('C',4,2,9),('D',1,5,12)],2,7,8)),
      ('S03','en','item_revision',spec([('A',1,2,4),('B',2,3,11),('C',3,4,9)],1,3,4)),
      ('S04','ko','limit_revision',spec([('A',4,2,11),('B',3,3,12),('C',1,3,6),('D',2,2,8)],2,5,8)),
      ('S05','en','unapproved_draft',spec([('A',2,3,4),('B',3,2,10),('C',4,3,11),('D',1,5,6)],2,7,9)),
      ('S06','ko','exclusion',spec([('A',3,4,21),('B',4,5,17),('C',5,6,14),('D',2,3,12)],1,6,8,['A'])),
      ('S07','en','dependency_conflict',spec([('A',4,4,15),('B',3,5,14),('C',3,4,13),('D',2,3,4),('E',2,3,9)],2,7,9,(),[('A','D')],[('B','C')])),
      ('S08','ko','true_tie',spec([('A',2,2,9),('B',2,2,9),('C',1,3,4),('D',3,1,5)],1,4,4)),
    ]
    out=[]
    for cid,lang,family,gold in definitions:
        ko=lang=='ko'; visible=copy.deepcopy(gold); notes=[]
        if family=='item_revision': visible['items'][0]['value']=20
        if family=='limit_revision': visible['time_limit']=9
        lines=[]
        def row(r,lid):
            return f'[{lid}] {r["id"]} | time={r["time"]} | cost={r["cost"]} | value={r["value"]}'
        for i,r in enumerate(visible['items'],1): lines.append(row(r,f'L{i:02}'))
        lines += [f'[R01] Pick exactly {visible["pick"]} distinct items.',
                  f'[R02] Total time <= {visible["time_limit"]}.',
                  f'[R03] Total cost <= {visible["cost_limit"]}.']
        if family=='item_revision':
            lines.append(row(gold['items'][0],'L04'))
            notes.append('Final correction: L04 replaces L01. All other records remain in force.')
        if family=='limit_revision':
            lines.append('[R04] Total time <= 5.')
            notes.append('최종 정정: R04가 R02를 대체한다. 다른 기록은 변경하지 않는다.')
        if family=='unapproved_draft':
            proposal=copy.deepcopy(gold['items'][0]);proposal['value']=60
            lines.append(row(proposal,'L05'))
            notes.append('L05 is an unapproved draft, not an effective correction. Keep L01.')
        for i,item in enumerate(gold['excluded'],4):lines.append(f'[R{i:02}] Exclude {item}.')
        for i,(a,b) in enumerate(gold['requires'],4):lines.append(f'[R{i:02}] {a} requires {b}.')
        for i,(a,b) in enumerate(gold['incompatible'],4+len(gold['requires'])):lines.append(f'[R{i:02}] {a} incompatible with {b}.')
        if ko:
            # Rule grammar remains bilingual-readable; authority notes and task are Korean.
            introduction='최종 지시와 현재 유효한 기록을 적용하라. time=시간, cost=비용, value=가치다. 정확한 선택 개수 및 모든 제한을 지키면서 가치 합계가 가장 큰 조합을 구하라. 최대값이 같으면 그중 어느 조합이나 허용한다. 명시하지 않은 다른 제한은 없다.'
        else:
            introduction='Apply the final instructions and currently effective records. Meet the exact selection count and every constraint; maximize total value. Any tied optimum is acceptable. There are no unstated constraints.'
        source=introduction+'\n'+'\n'.join(lines)+'\n'+'\n'.join(notes)
        out.append({'id':cid,'language':lang,'family':family,'source':source,'gold':gold})
    return out

def no_duplicates(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError('DUPLICATE_KEY')
        d[k]=v
    return d

def parse(text):
    decoder=json.JSONDecoder(object_pairs_hook=no_duplicates)
    stripped=text.strip()
    try: return decoder.decode(stripped),True
    except (ValueError,json.JSONDecodeError): pass
    # Only maximal JSON objects; nested objects are consumed with their parent.
    objects=[];offset=0
    while offset<len(text):
        at=text.find('{',offset)
        if at<0:break
        try:
            obj,n=decoder.raw_decode(text[at:]);objects.append(obj);offset=at+n
        except ValueError:
            # A malformed outer object must not be salvaged from a nested fragment.
            return None,False
    return (objects[0],False) if len(objects)==1 else (None,False)

def normalize(s):
    if not isinstance(s,dict) or set(s)!=FIELDS: raise ValueError('SPEC_KEYS')
    s=copy.deepcopy(s)
    if not isinstance(s['items'],list) or not 1<=len(s['items'])<=12: raise ValueError('ITEM_COUNT')
    ids=[]
    for r in s['items']:
        if not isinstance(r,dict) or set(r)!={'id','time','cost','value'}:raise ValueError('ITEM_SCHEMA')
        if not isinstance(r['id'],str) or not re.fullmatch('[A-Z]',r['id']):raise ValueError('ITEM_ID')
        if any(type(r[k]) is not int or not 0<=r[k]<=10000 for k in ['time','cost','value']):raise ValueError('ITEM_NUMBER')
        ids.append(r['id'])
    if len(ids)!=len(set(ids)):raise ValueError('DUPLICATE_ITEM')
    for key in ['pick','time_limit','cost_limit']:
        if type(s[key]) is not int or not 0<=s[key]<=10000:raise ValueError('RULE_NUMBER')
    if not 1<=s['pick']<=len(ids):raise ValueError('PICK_RANGE')
    if not isinstance(s['excluded'],list) or any(not isinstance(i,str) or i not in ids for i in s['excluded']):raise ValueError('EXCLUDED')
    if len(set(s['excluded']))!=len(s['excluded']):raise ValueError('EXCLUDED_DUPLICATE')
    for k in ['requires','incompatible']:
        if not isinstance(s[k],list):raise ValueError('PAIR_LIST')
        pairs=[]
        for p in s[k]:
            if not isinstance(p,list) or len(p)!=2 or any(not isinstance(i,str) or i not in ids for i in p) or p[0]==p[1]:raise ValueError('PAIR_SCHEMA')
            pairs.append(p if k=='requires' else sorted(p))
        if len({tuple(p) for p in pairs})!=len(pairs):raise ValueError('PAIR_DUPLICATE')
        s[k]=sorted(pairs)
    s['items']=sorted(s['items'],key=lambda x:x['id']);s['excluded']=sorted(s['excluded'])
    return s

def registry(source):
    records={}
    for line in source.splitlines():
        m=re.fullmatch(r'\[([LR]\d+)\] (.*)',line)
        if not m:continue
        ref,body=m.groups()
        if ref in records:raise ValueError('DUPLICATE_SOURCE_REF')
        item=re.fullmatch(r'([A-Z]) \| time=(\d+) \| cost=(\d+) \| value=(\d+)',body)
        if item:
            i,t,c,v=item.groups();records[ref]=('item',dict(id=i,time=int(t),cost=int(c),value=int(v)));continue
        formats=[('pick',r'Pick exactly (\d+) distinct items\.'),('time_limit',r'Total time <= (\d+)\.'),('cost_limit',r'Total cost <= (\d+)\.')]
        for k,pattern in formats:
            hit=re.fullmatch(pattern,body)
            if hit:records[ref]=(k,int(hit[1]));break
        if ref in records:continue
        hit=re.fullmatch(r'Exclude ([A-Z])\.',body)
        if hit:records[ref]=('excluded',hit[1]);continue
        for k,pattern in [('requires',r'([A-Z]) requires ([A-Z])\.'),('incompatible',r'([A-Z]) incompatible with ([A-Z])\.')]:
            hit=re.fullmatch(pattern,body)
            if hit:records[ref]=(k,list(hit.groups()));break
        if ref not in records:raise ValueError('UNSUPPORTED_SOURCE_GRAMMAR')
    return records

def assemble(source,refs):
    if not isinstance(refs,dict) or set(refs)!={'item_refs','rule_refs'}:raise ValueError('REF_KEYS')
    r=registry(source); s={'items':[],'excluded':[],'requires':[],'incompatible':[]}
    for part in ['item_refs','rule_refs']:
        values=refs[part]
        if not isinstance(values,list) or any(not isinstance(x,str) for x in values) or len(values)!=len(set(values)):raise ValueError('REF_LIST')
        for ref in values:
            if ref not in r:raise ValueError('UNKNOWN_REFERENCE')
            k,v=r[ref]
            if (part=='item_refs')!=(k=='item'):raise ValueError('WRONG_REFERENCE_KIND')
            if k=='item':s['items'].append(copy.deepcopy(v))
            elif k in ('excluded','requires','incompatible'):s[k].append(copy.deepcopy(v))
            else:
                if k in s:raise ValueError('AMBIGUOUS_RULE')
                s[k]=v
    # No hidden oracle or authority-note interpretation here. Fidelity is a separate score.
    return normalize(s)

def solve(s):
    s=normalize(s);checked=0;best=None;answer=None
    for group in itertools.combinations(s['items'],s['pick']):
        checked+=1;ids={r['id'] for r in group}
        if ids.intersection(s['excluded']):continue
        if any(a in ids and b not in ids for a,b in s['requires']):continue
        if any(a in ids and b in ids for a,b in s['incompatible']):continue
        totals={k:sum(r[k] for r in group) for k in ('time','cost','value')}
        if totals['time']>s['time_limit'] or totals['cost']>s['cost_limit']:continue
        if best is None or totals['value']>best:
            best=totals['value'];answer={'selected':sorted(ids),**totals}
    return answer,checked

def oracle(s):
    """Independent mask-based scorer; never called by source compiler or solver."""
    options=s['items'];winners=[];best=None
    for mask in range(1<<len(options)):
        idx=[i for i in range(len(options)) if mask&(1<<i)]
        if len(idx)!=s['pick']:continue
        selected=[options[i]['id'] for i in idx]
        if any(i in selected for i in s['excluded']):continue
        if any((a in selected) and (b not in selected) for a,b in s['requires']):continue
        if any((a in selected) and (b in selected) for a,b in s['incompatible']):continue
        tm=0;cost=0;value=0
        for i in idx:tm+=options[i]['time'];cost+=options[i]['cost'];value+=options[i]['value']
        if tm>s['time_limit'] or cost>s['cost_limit']:continue
        if best is None or value>best:best=value;winners=[]
        if value==best:winners.append({'selected':sorted(selected),'time':tm,'cost':cost,'value':value})
    return winners

def score_answer(gold,answer):
    if not isinstance(answer,dict) or set(answer)!=ANSWER_FIELDS:return None
    ids=answer['selected']
    if not isinstance(ids,list) or any(not isinstance(i,str) for i in ids):return None
    if any(type(answer[k]) is not int for k in ('time','cost','value')):return None
    obj=copy.deepcopy(answer);obj['selected']=sorted(ids)
    return obj in oracle(gold)

def prompt(task,arm):
    common=task['source']+'\n\n'
    if arm=='DIRECT':
        return common+'Return the optimal selection and its totals, using exactly this JSON schema: {"selected":["A"],"time":0,"cost":0,"value":0}. No tool is available in this diagnostic arm.'
    if arm=='VALUE_TOOL':
        return common+'A deterministic solver will perform all calculations and optimization. Do NOT solve or select items yourself. Transfer ALL currently effective items and constraints to this exact JSON schema; empty constraint lists are allowed when absent. Do not omit unselected items. Do not include replaced or unapproved records. Schema: {"items":[{"id":"A","time":0,"cost":0,"value":0}],"pick":1,"time_limit":0,"cost_limit":0,"excluded":[],"requires":[],"incompatible":[]}. requires and incompatible contain ID pairs like ["A","B"].'
    return common+'The SAME deterministic solver will perform all calculations and optimization. Do NOT solve, copy numbers, or select items yourself. Return references to ALL currently effective item rows and ALL currently effective rule rows. Do not omit unselected items. Do not include replaced or unapproved records. The program will copy the exact referenced facts into the solver. Schema: {"item_refs":["L01","L02"],"rule_refs":["R01","R02","R03"]}.'

def assess(task,arm,response):
    obj,json_format=parse(response['text']);s=None;answer=None;error=None;checks=0;source_fidelity=None
    start=time.monotonic()
    try:
        if arm=='DIRECT':
            answer=obj;schema_ok=(isinstance(obj,dict) and set(obj)==ANSWER_FIELDS and isinstance(obj.get('selected'),list) and all(isinstance(i,str) for i in obj['selected']) and all(type(obj.get(k)) is int for k in ('time','cost','value')))
        else:
            s=normalize(obj) if arm=='VALUE_TOOL' else assemble(task['source'],obj)
            schema_ok=True;answer,checks=solve(s)
    except (ValueError,TypeError,KeyError) as exc:
        schema_ok=False;error=str(exc)[:200]
    tool_ms=round((time.monotonic()-start)*1000,4)
    score_start=time.monotonic()
    source_fidelity=(s==normalize(task['gold'])) if s is not None else None
    semantic=score_answer(task['gold'],answer)
    natural_end=response.get('finish_reason')=='stop'
    fmt=json_format and schema_ok
    return {'semantic_pass':semantic,'format_pass':fmt,'case_pass':semantic is True and fmt and natural_end,
            'source_fidelity':source_fidelity,'wrong_spec_right_answer':source_fidelity is False and semantic is True,
            'compiled_spec':s,'answer':answer,'tool_error':error,'checked_combinations':checks,
            'tool_ms':tool_ms,'scorer_ms':round((time.monotonic()-score_start)*1000,4),'natural_end':natural_end}

def controls(tasks):
    result=[]
    for t in tasks:
        reg=registry(t['source']);refs={'item_refs':[r for r,(k,v) in reg.items() if k=='item'],
                                     'rule_refs':[r for r,(k,v) in reg.items() if k!='item']}
        try:
            s=assemble(t['source'],refs);a,n=solve(s);error=None
            fidelity=s==normalize(t['gold'])
        except ValueError as e:a=None;n=0;error=str(e);fidelity=None
        # Positive solver calibration is NOT a candidate arm: receives exact gold spec.
        oracle_answer,_=solve(t['gold'])
        result.append({'case_id':t['id'],'no_model_all_rows_answer':a,'all_rows_semantic_pass':score_answer(t['gold'],a),
          'all_rows_error':error,'all_rows_source_fidelity':fidelity,'all_rows_checked':n,
          'positive_solver_control_pass':score_answer(t['gold'],oracle_answer),'model_calls':0})
    return result

def summarize(records,health,identity,errors,started,start,control_rows):
    arms={}
    for arm in ARMS:
        rs=[r for r in records if r['arm']==arm];passed=sum(r['score']['semantic_pass'] is True for r in rs)
        unknown=sum(r['score']['semantic_pass'] is None for r in rs)
        arms[arm]={'n':len(rs),'semantic_pass':passed,'unscorable':unknown,
          'semantic_bounds': [passed/len(rs),(passed+unknown)/len(rs)] if rs else None,
          'format_pass':sum(r['score']['format_pass'] for r in rs),'case_pass':sum(r['score']['case_pass'] for r in rs),
          'source_fidelity_pass':None if arm=='DIRECT' else sum(r['score']['source_fidelity'] is True for r in rs),
          'wrong_spec_right_answer':sum(r['score']['wrong_spec_right_answer'] for r in rs),
          'total_tokens':sum((r['response'].get('usage') or {}).get('total_tokens',0) for r in rs),
          'prompt_tokens':sum((r['response'].get('usage') or {}).get('prompt_tokens',0) for r in rs),
          'completion_tokens':sum((r['response'].get('usage') or {}).get('completion_tokens',0) for r in rs),
          'unknown_usage':sum(not r['response'].get('usage') for r in rs),
          'model_calls':len(rs),'median_ms':statistics.median(r['response']['elapsed_ms']+r['score']['tool_ms'] for r in rs) if rs else None}
    return {'experiment':EXPERIMENT,'status':'COMPLETE' if len(records)==48 and not errors else 'INCOMPLETE',
            'model':identity,'arms':arms,'health':health,'controls':control_rows,'errors':errors,
            'actual_model_calls_started':started,'actual_model_calls_completed':len(records)+len(health),
            'known_physical_tokens':sum((r['response'].get('usage') or {}).get('total_tokens',0) for r in records+health),
            'elapsed_ms':round((time.monotonic()-start)*1000,2),'user_manual_test_steps':0,
            'promotion':'NOT_PROMOTED','limits':'8 fresh constructed sources, 4 Korean tasks with English record grammar; two seeds each. Ref vs Value share solver but not prompt length. Exact generic solver is an allowed operational tool here, not hidden oracle feedback. No real company/Max reference evaluation.'}

def execute(out):
    out.mkdir(parents=True,exist_ok=True)
    if (out/'events.jsonl').exists():raise RuntimeError('OUTPUT_EXISTS_REFUSE_OVERWRITE')
    tasks=cases();start=time.monotonic();records=[];health=[];identity={};errors=[];calls=0;proc=None
    control_rows=controls(tasks);store(out/'cases.json',tasks);store(out/'controls.json',control_rows)
    registration={'experiment':EXPERIMENT,'cases_sha256':digest(tasks),'script_sha256':transport.file_sha(__file__),
      'arms':ARMS,'primary_pair':['VALUE_TOOL','REF_TOOL'],'repeats':2,'maximum_calls':52,
      'budget_seconds':BUDGET_SECONDS,'request_timeout_seconds':transport.TIMEOUT,'client_max_tokens':None,
      'same_solver':True,'feedback_or_repair_calls':0,'hidden_gold_in_model_prompts':False,
      'source_adapter':'controlled line grammar only; no generic document understanding claim',
      'arm_order':'rotating 3-arm order per case; second repeat reverses first order',
      'gate':'four existing canaries pass semantic, format and natural end before new sources',
      'promotion_rule':'screen only; no global promotion without fresh distribution and source fidelity validation',
      'user_manual_test_steps':0,'company_and_max_reference':'NOT_MEASURED'}
    store(out/'registration.json',registration)
    def checkpoint():store(out/'summary.json',summarize(records,health,identity,errors,calls,start,control_rows))
    def record_event(event):
        with (out/'events.jsonl').open('a',encoding='utf-8') as f:f.write(canonical(event)+'\n');f.flush();os.fsync(f.fileno())
    with tempfile.TemporaryDirectory(prefix='qwen-source-') as tmp:
        work=pathlib.Path(tmp)
        try:
            proc,identity=instrument.provision(work,out)
            identity['study_sha256']=transport.file_sha(__file__);store(out/'identity.json',identity)
            for idx,(name,text,expected) in enumerate(instrument.HEALTH):
                calls+=1;messages=[{'role':'system','content':transport.BASE_SYSTEM},{'role':'user','content':text}]
                record_event({'event':'start','kind':'canary','id':name,'request':messages,'seed':9300+idx})
                rr=transport.infer(messages,9300+idx);o,f=parse(rr['text'])
                value=o.get('answer') if isinstance(o,dict) else None
                entry={'id':name,'response':rr,'pass':type(value)==type(expected) and value==expected and f and rr['finish_reason']=='stop'}
                health.append(entry);record_event({'event':'complete','kind':'canary','record':entry});checkpoint()
            if not all(x['pass'] for x in health):raise RuntimeError('CANARY_FAILED_NO_ARCHITECTURE_CONCLUSION')
            for rep in range(REPEATS):
                for idx,t in enumerate(tasks):
                    order=ARMS[idx%3:]+ARMS[:idx%3]
                    if rep:order=list(reversed(order))
                    for arm in order:
                        if time.monotonic()-start>BUDGET_SECONDS:raise TimeoutError('STUDY_BUDGET')
                        messages=[{'role':'system','content':BASE},{'role':'user','content':prompt(t,arm)}]
                        seed=42000+100*rep+idx;calls+=1
                        record_event({'event':'start','kind':'study','case_id':t['id'],'arm':arm,'repeat':rep+1,'request':messages,'seed':seed})
                        rr=transport.infer(messages,seed)
                        entry={'case_id':t['id'],'family':t['family'],'language':t['language'],'arm':arm,'repeat':rep+1,
                               'response':rr,'score':assess(t,arm,rr)}
                        records.append(entry);record_event({'event':'complete','kind':'study','record':entry});checkpoint()
                        print('SOURCE_RESULT '+canonical({'id':t['id'],'arm':arm,'repeat':rep+1,'score':entry['score'], 'tokens':rr.get('usage')}),flush=True)
        except Exception as exc:
            errors.append({'class':type(exc).__name__,'detail':str(exc)[:500],'calls_started':calls});checkpoint()
        finally:
            if proc:
                proc.terminate()
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
            if (work/'server.log').exists():shutil.copyfile(work/'server.log',out/'server.log')
    checkpoint();print('FINAL_SOURCE '+canonical(summarize(records,health,identity,errors,calls,start,control_rows)),flush=True)
    if errors:raise SystemExit(2)

class Tests(unittest.TestCase):
    def test_case_count(self):self.assertEqual(len(cases()),8)
    def test_language_balance(self):self.assertEqual(sum(t['language']=='ko' for t in cases()),4)
    def test_determinism(self):self.assertEqual(cases(),cases())
    def test_gold_solver(self):self.assertTrue(all(score_answer(t['gold'],solve(t['gold'])[0]) for t in cases()))
    def test_two_solvers_random(self):
        import random
        rng=random.Random(992)
        for i in range(200):
            s=spec([(chr(65+j),rng.randint(1,9),rng.randint(1,9),rng.randint(1,15)) for j in range(6)],2,12,11)
            a,_=solve(s);g=oracle(s)
            self.assertTrue(a in g if g else a is None)
    def test_tie(self):self.assertEqual(len(oracle(cases()[-1]['gold'])),2)
    def test_exclusion(self):self.assertNotIn('A',solve(cases()[5]['gold'])[0]['selected'])
    def test_revision_ref(self):
        t=cases()[2];s=assemble(t['source'],{'item_refs':['L02','L03','L04'],'rule_refs':['R01','R02','R03']})
        self.assertEqual(s,normalize(t['gold']))
    def test_limit_ref(self):
        t=cases()[3];s=assemble(t['source'],{'item_refs':['L01','L02','L03','L04'],'rule_refs':['R01','R03','R04']})
        self.assertEqual(s,normalize(t['gold']))
    def test_draft_ref(self):
        t=cases()[4];s=assemble(t['source'],{'item_refs':['L01','L02','L03','L04'],'rule_refs':['R01','R02','R03']})
        self.assertEqual(s,normalize(t['gold']))
    def test_unknown_ref(self):
        with self.assertRaises(ValueError):assemble(cases()[0]['source'],{'item_refs':['L99'],'rule_refs':['R01','R02','R03']})
    def test_duplicate_ref(self):
        with self.assertRaises(ValueError):assemble(cases()[0]['source'],{'item_refs':['L01','L01'],'rule_refs':['R01','R02','R03']})
    def test_ambiguous_item(self):
        with self.assertRaises(ValueError):assemble(cases()[2]['source'],{'item_refs':['L01','L02','L03','L04'],'rule_refs':['R01','R02','R03']})
    def test_missing_budget(self):
        with self.assertRaises(ValueError):assemble(cases()[0]['source'],{'item_refs':['L01','L02','L03'],'rule_refs':['R01','R02']})
    def test_wrong_rule_kind(self):
        with self.assertRaises(ValueError):assemble(cases()[0]['source'],{'item_refs':['R01'],'rule_refs':['R02','R03']})
    def test_nested_parse(self):self.assertEqual(parse('{"items":[{"id":"A"}]}')[0],{'items':[{'id':'A'}]})
    def test_fence_parse(self):self.assertEqual(parse('```json\n{"x":1}\n```'),({'x':1},False))
    def test_two_objects(self):self.assertEqual(parse('{"x":1} {"x":2}'),(None,False))
    def test_duplicate_json_key(self):self.assertEqual(parse('{"x":1,"x":2}'),(None,False))
    def test_bool_reject(self):
        s=copy.deepcopy(cases()[0]['gold']);s['pick']=True
        with self.assertRaises(ValueError):normalize(s)
    def test_numeric_corruption_fidelity(self):
        t=cases()[0];s=copy.deepcopy(t['gold']);s['items'][0]['value']+=1
        r=assess(t,'VALUE_TOOL',{'text':canonical(s),'finish_reason':'stop'})
        self.assertFalse(r['source_fidelity']);self.assertTrue(r['wrong_spec_right_answer'])
    def test_all_rows_has_negative_control(self):
        c=controls(cases());self.assertEqual(sum(x['all_rows_error'] is not None for x in c),3)
    def test_no_oracle_in_tool(self):
        for f in [assemble,solve,registry,normalize]:self.assertNotIn('oracle',f.__code__.co_names)
    def test_no_gold_serialized(self):
        for t in cases():
            for arm in ARMS:self.assertNotIn('"gold"',prompt(t,arm))
    def test_natural_end(self):
        t=cases()[0];r=assess(t,'DIRECT',{'text':canonical(solve(t['gold'])[0]),'finish_reason':'length'})
        self.assertFalse(r['case_pass'])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--out',default='results/source_protocol_v1_live');args=ap.parse_args()
    if args.self_test:unittest.main(argv=[sys.argv[0]],exit=True)
    else:execute(pathlib.Path(args.out))
