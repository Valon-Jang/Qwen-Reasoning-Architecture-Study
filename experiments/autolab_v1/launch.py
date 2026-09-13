#!/usr/bin/env python3
"""Acquisition-only repair after run 34755221135 failed HTTP 401 before inference.
No changes to cases, prompts, scoring or inference parameters. The job-scoped
GitHub token is sent only to api.github.com, never to model downloads or server.
"""
import json, os, pathlib, sys, time, urllib.error, urllib.parse, urllib.request
import run as pilot
OUT=pathlib.Path('results/autolab_v1_live')
OUT.mkdir(parents=True,exist_ok=True)
original_download=pilot.download
GH_TOKEN=os.environ.pop('GITHUB_TOKEN','')

def read_url(url, timeout=60):
    parts=urllib.parse.urlsplit(url)
    headers={'User-Agent':'Qwen-Reasoning-Architecture-Study/Autolab-v1'}
    token=GH_TOKEN
    if parts.hostname=='api.github.com' and token:
        headers['Authorization']='Bearer '+token
        headers['Accept']='application/vnd.github+json'
    print('ACQUIRE_READ '+parts.scheme+'://'+parts.netloc+parts.path,flush=True)
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError('ACQUIRE_HTTP_'+str(exc.code)+' '+parts.netloc+parts.path) from exc

def download(url, path, expected=None, limit=1200000000):
    parts=urllib.parse.urlsplit(url)
    print('ACQUIRE_DOWNLOAD '+parts.netloc+parts.path,flush=True)
    try:
        return original_download(url,path,expected,limit)
    except urllib.error.HTTPError as exc:
        raise RuntimeError('DOWNLOAD_HTTP_'+str(exc.code)+' '+parts.netloc+parts.path) from exc

pilot.read_url=read_url
pilot.download=download
original_provision=pilot.provision

def provision(work,out):
    proc,identity=original_provision(work,out)
    identity['transport_launcher_sha256']=pilot.file_sha(__file__)
    # Do not retain job token in inference-server or model-facing scope.
    pilot.write(out/'identity.json',identity)
    return proc,identity

pilot.provision=provision
pilot.write(OUT/'transport_change.json',{'prior_run':34755221135,'reason':'HTTP 401 before first inference; original missing-stage diagnostics insufficient',
    'change':'job-scoped GitHub API authentication plus acquisition-stage diagnostics',
    'scope':'transport-only, no experiment change','launcher_sha256':pilot.file_sha(__file__)})
pilot.run(OUT)
