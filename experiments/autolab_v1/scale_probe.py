#!/usr/bin/env python3
"""Bounded 2B instrument qualification. No architecture promotion from canaries."""
import json, os, pathlib, shutil, subprocess, tarfile, tempfile, time, urllib.request
import run as pilot
from calibrate import HEALTH, concrete

MODEL_URL='https://huggingface.co/unsloth/Qwen3.5-2B-GGUF/resolve/main/Qwen3.5-2B-Q8_0.gguf'
MODEL_SHA='1b04acba824817554f4ce23639bc8495ff70453b8fcb047900c731521021f2c1'
TOKEN=os.environ.pop('GITHUB_TOKEN','')
pilot.MODEL_SOURCE='Qwen/Qwen3.5-2B'
EXPERIMENT='Q35_2B_INSTRUMENT_CALIBRATION_V1'

def provision(work,out):
    headers={'User-Agent':'Qwen-Architecture-Study/2B-Probe','Accept':'application/vnd.github+json'}
    if TOKEN:headers['Authorization']='Bearer '+TOKEN
    request=urllib.request.Request('https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/'+pilot.LLAMA_TAG,headers=headers)
    with urllib.request.urlopen(request,timeout=30) as response:release=json.load(response)
    asset=next(a for a in release['assets'] if a['name']==f'llama-{pilot.LLAMA_TAG}-bin-ubuntu-x64.tar.gz')
    assert asset['digest'].startswith('sha256:')
    print('STAGE runtime_download',flush=True)
    runtime=pilot.download(asset['browser_download_url'],work/'runtime.tar.gz',asset['digest'][7:],500000000)
    with tarfile.open(work/'runtime.tar.gz') as tf:tf.extractall(work/'runtime',filter='data')
    binary=next((work/'runtime').rglob('llama-server'));binary.chmod(binary.stat().st_mode|0o111)
    print('STAGE 2B_weight_download',flush=True)
    weights=pilot.download(MODEL_URL,work/'model.gguf',MODEL_SHA,3000000000)
    env=os.environ.copy();env['LD_LIBRARY_PATH']=str(binary.parent)+':'+env.get('LD_LIBRARY_PATH','')
    assert 'GITHUB_TOKEN' not in env
    version=subprocess.check_output([str(binary),'--version'],env=env,stderr=subprocess.STDOUT,text=True,timeout=20)
    identity={'model':'Qwen/Qwen3.5-2B','model_repo':'unsloth/Qwen3.5-2B-GGUF','model_file':'Qwen3.5-2B-Q8_0.gguf',
      'weights':weights,'runtime_asset':runtime,'runtime_version':version,'binary_sha256':pilot.file_sha(binary),
      'script_sha256':pilot.file_sha(__file__),'inference_helper_sha256':pilot.file_sha(pilot.__file__),
      'git_commit':os.getenv('GITHUB_SHA'),'run_id':os.getenv('GITHUB_RUN_ID'),
      'thinking':False,'temperature':0.6,'top_p':0.95,'top_k':20,'context_tokens':8192,
      'client_max_tokens':None,'request_timeout_seconds':100,'device':'CPU','threads':4,
      'company_deployment':'NOT_MEASURED','target_reference':'NOT_MEASURED'}
    pilot.write(out/'identity.json',identity);print('MODEL_IDENTITY '+pilot.dumps(identity),flush=True)
    logfile=open(work/'server.log','w')
    proc=subprocess.Popen([str(binary),'-m',str(work/'model.gguf'),'--host','127.0.0.1','--port','8080','-c','8192','-t','4','-np','1','-ngl','0','-n','-1','--jinja','--chat-template-kwargs','{"enable_thinking":false}'],env=env,stdout=logfile,stderr=subprocess.STDOUT)
    try:
        for _ in range(120):
            if proc.poll() is not None:raise RuntimeError('SERVER_EXIT')
            try:
                if pilot.api('http://127.0.0.1:8080/health').get('status')=='ok':return proc,identity
            except Exception:pass
            time.sleep(1)
        raise RuntimeError('SERVER_START_TIMEOUT')
    except BaseException:
        proc.terminate()
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        raise

def main():
    out=pathlib.Path('results/autolab_v1_live');out.mkdir(parents=True,exist_ok=True)
    pilot.write(out/'scale_registration.json',{'experiment':EXPERIMENT,'reason':'0.8B basic controls 2/4 and hard-task floor',
      'health_cases':HEALTH,'health_repeats':2,'pass_gate':'all 8 semantic AND format pass, each finish_reason=stop',
      'conditional_hard_screen':'only after 8/8 gate: P01..P04 CONCRETE_TEXT, development only',
      'maximum_model_calls':12,'no_user_test_steps':True,'no_architecture_change':True,
      'weight_sha256':MODEL_SHA,'prior_08b_calibration_run':34756276184})
    start=time.monotonic();proc=None;health=[];hard=[];errors=[];identity={};calls=0
    def save():
        healthpass=sum(x['pass'] for x in health)
        gate=len(health)==8 and healthpass==8
        complete=len(health)==8 and (not gate or len(hard)==4) and not errors
        result={'experiment':EXPERIMENT,'status':'COMPLETE' if complete else 'INCOMPLETE','model':identity,
          'health':health,'health_pass':healthpass,'health_runs':len(health),'health_gate':'PASS' if gate else 'NOT_PASSED',
          'hard_screen':hard,'hard_pass':sum(x['score']['case_pass'] for x in hard),'hard_runs':len(hard),
          'actual_model_calls_started':calls,'known_total_tokens':sum((x['response'].get('usage') or {}).get('total_tokens',0) for x in health+hard),
          'usage_unknown':sum(not x['response'].get('usage') for x in health+hard),
          'errors':errors,'research_elapsed_ms':round((time.monotonic()-start)*1000,2),'promotion':'NOT_PROMOTED',
          'user_manual_test_steps':0,'interpretation':'canary gate only, not proof of target-task adequacy or Max equivalence'}
        pilot.write(out/'scale_summary.json',result);return result
    with tempfile.TemporaryDirectory(prefix='qwen-scale-') as td:
        work=pathlib.Path(td)
        try:
            proc,identity=provision(work,out)
            for rep in range(2):
                for idx,(name,text,expected) in enumerate(HEALTH):
                    if time.monotonic()-start>1000:raise TimeoutError('RESEARCH_BUDGET')
                    calls+=1;response=pilot.infer([{'role':'system','content':pilot.BASE_SYSTEM},{'role':'user','content':text}],7300+100*rep+idx)
                    obj,fmt=pilot.parse(response['text']);value=obj.get('answer') if isinstance(obj,dict) else None
                    semantic=type(value)==type(expected) and value==expected
                    health.append({'id':name,'repeat':rep+1,'prompt':text,'expected':expected,'response':response,
                      'semantic_pass':semantic,'format_pass':fmt,'pass':semantic and fmt and response['finish_reason']=='stop'})
                    print('SCALE_HEALTH '+pilot.dumps(health[-1]),flush=True);save()
            if all(x['pass'] for x in health):
                tasks=pilot.cases()[:4];pilot.write(out/'hard_cases.json',tasks)
                for idx,task in enumerate(tasks):
                    if time.monotonic()-start>1000:raise TimeoutError('RESEARCH_BUDGET')
                    text=concrete(task);calls+=1
                    response=pilot.infer([{'role':'system','content':pilot.BASE_SYSTEM},{'role':'user','content':text}],20260913+idx)
                    score=pilot.score(task,response['text']) if response['finish_reason']=='stop' else {'semantic_pass':None,'format_pass':False,'case_pass':False}
                    hard.append({'id':task['id'],'prompt':text,'response':response,'score':score})
                    print('SCALE_HARD '+pilot.dumps(hard[-1]),flush=True);save()
        except Exception as exc:errors.append({'class':type(exc).__name__,'detail':str(exc)[:600]})
        finally:
            if proc:
                proc.terminate()
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
            if (work/'server.log').exists():shutil.copyfile(work/'server.log',out/'server.log')
    print('FINAL_SCALE '+pilot.dumps(save()),flush=True)
    if errors:raise SystemExit(2)

if __name__=='__main__':main()
