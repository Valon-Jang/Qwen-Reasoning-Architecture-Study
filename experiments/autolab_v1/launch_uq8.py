#!/usr/bin/env python3
"""Replanned instrument: public Unsloth Q8, checksum-pinned before inference.
Reuses the tested pilot cases, independent scorer and model request code.
The failed ggerganov HF API path is NOT retried. No private/company data.
"""
import json, os, pathlib, subprocess, tarfile, time, urllib.request, urllib.parse
import run as pilot

OUT=pathlib.Path('results/autolab_v1_live')
MODEL_URL='https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF/resolve/main/Qwen3.5-0.8B-Q8_0.gguf'
MODEL_SHA='0ad885ffd4bb022fc4f0d33a3308fa108ef8613159d3b3a67e23abca056b7a6c'
PUBLISHER_PAGE='https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF/blob/main/Qwen3.5-0.8B-Q8_0.gguf'
TOKEN=os.environ.pop('GITHUB_TOKEN','')
pilot.EXPERIMENT='Q35_SMALL_REAL_FEEDBACK_UQ8_V2'
pilot.MODEL_REPO='unsloth/Qwen3.5-0.8B-GGUF'


def provision(work,out):
    stage='runtime_metadata'
    proc=None
    try:
        headers={'User-Agent':'Qwen-Reasoning-Architecture-Study/Autolab-v2','Accept':'application/vnd.github+json'}
        if TOKEN: headers['Authorization']='Bearer '+TOKEN
        request=urllib.request.Request('https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/'+pilot.LLAMA_TAG,headers=headers)
        with urllib.request.urlopen(request,timeout=30) as r: release=json.load(r)
        filename=f'llama-{pilot.LLAMA_TAG}-bin-ubuntu-x64.tar.gz'
        assets=[a for a in release['assets'] if a['name']==filename]
        if len(assets)!=1: raise RuntimeError('EXACT_RUNTIME_ASSET_NOT_FOUND')
        asset=assets[0]; digest=asset.get('digest','')
        if not digest.startswith('sha256:'): raise RuntimeError('RUNTIME_PUBLISHER_HASH_MISSING')
        stage='runtime_download'; print('STAGE '+stage,flush=True)
        rt=pilot.download(asset['browser_download_url'],work/'runtime.tar.gz',digest[7:],500000000)
        with tarfile.open(work/'runtime.tar.gz') as tf: tf.extractall(work/'runtime',filter='data')
        bins=list((work/'runtime').rglob('llama-server'))
        if len(bins)!=1: raise RuntimeError('RUNTIME_BINARY_AMBIGUOUS')
        binary=bins[0]; binary.chmod(binary.stat().st_mode|0o111)
        stage='public_unsloth_checksum_pinned_download'; print('STAGE '+stage,flush=True)
        w=pilot.download(MODEL_URL,work/'model.gguf',MODEL_SHA)
        stage='runtime_contract'
        env=os.environ.copy(); env['LD_LIBRARY_PATH']=str(binary.parent)+':'+env.get('LD_LIBRARY_PATH','')
        assert 'GITHUB_TOKEN' not in env
        version=subprocess.check_output([str(binary),'--version'],env=env,stderr=subprocess.STDOUT,text=True,timeout=20)
        helptext=subprocess.check_output([str(binary),'--help'],env=env,stderr=subprocess.STDOUT,text=True,timeout=20)
        for flag in ('--jinja','--chat-template-kwargs'):
            if flag not in helptext: raise RuntimeError('RUNTIME_FLAG_UNSUPPORTED:'+flag)
        identity={'base_model':pilot.MODEL_SOURCE,'model_repo':pilot.MODEL_REPO,'model_file':'Qwen3.5-0.8B-Q8_0.gguf',
            'model_revision':'content-addressed SHA-256; branch URL accepted only if bytes match pinned hash',
            'weights':w,'publisher_checksum_page':PUBLISHER_PAGE,'runtime_release':pilot.LLAMA_TAG,'runtime_version':version,
            'runtime_asset':filename,'runtime_asset_hash':rt,'binary_sha256':pilot.file_sha(binary),
            'inference_device':'CPU','threads':4,'thinking':False,'temperature':0.6,'top_p':0.95,'top_k':20,
            'context_tokens':8192,'client_max_tokens':None,'server_n_predict':-1,'request_timeout_seconds':pilot.TIMEOUT,
            'script_sha256':pilot.file_sha(pilot.__file__),'launcher_sha256':pilot.file_sha(__file__),
            'git_commit':os.getenv('GITHUB_SHA'),'github_run_id':os.getenv('GITHUB_RUN_ID'),
            'target_reference':'NOT_MEASURED','company_deployment':'NOT_MEASURED'}
        pilot.write(out/'identity.json',identity); print('MODEL_IDENTITY '+pilot.dumps(identity),flush=True)
        stage='server_start'
        log=open(work/'server.log','w')
        cmd=[str(binary),'-m',str(work/'model.gguf'),'--host','127.0.0.1','--port','8080','-c','8192','-t','4','-np','1','-ngl','0','-n','-1','--jinja','--chat-template-kwargs','{"enable_thinking":false}']
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
        for _ in range(120):
            if proc.poll() is not None:
                print((work/'server.log').read_text()[-6000:],flush=True); raise RuntimeError('SERVER_EXIT')
            try:
                if pilot.api('http://127.0.0.1:8080/health').get('status')=='ok': return proc,identity
            except Exception: pass
            time.sleep(1)
        raise RuntimeError('SERVER_START_TIMEOUT')
    except Exception as e:
        if proc:
            proc.terminate()
            try: proc.wait(timeout=10)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()
        pilot.write(out/'acquisition_failure.json',{'stage':stage,'class':type(e).__name__,'detail':str(e)[:600], 'inference_calls':0})
        raise RuntimeError(stage+': '+type(e).__name__+': '+str(e)[:600]) from e

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    pilot.write(OUT/'instrument_registration.json',{'experiment':pilot.EXPERIMENT,'change':'different independently published quantization; not byte-identical to unavailable ggerganov artifact',
        'source':PUBLISHER_PAGE,'weight_sha256':MODEL_SHA,'unchanged':'tasks, scorer, prompts, temperatures, shared-prefix comparison',
        'previous_attempts':[34755221135,34755462416],'previous_condition':'acquisition failed before any inference; no result pooling',
        'manual_user_test_steps':0,'paid_inference':False})
    pilot.provision=provision
    pilot.run(OUT)
