#!/usr/bin/env python3
"""Build, verify, push the existing Sites source and package its exact commit.
Credential JSON is accepted only through hidden stdin. Native Sites tools save/publish
this returned commit and archive; this helper cannot publish by itself.
"""
from pathlib import Path
import json, os, subprocess, sys, tarfile, termios
ROOT=Path(__file__).resolve().parents[1]
if sys.stdin.isatty():
 attributes=termios.tcgetattr(sys.stdin);attributes[3]&=~termios.ECHO
 termios.tcsetattr(sys.stdin,termios.TCSANOW,attributes)
print('Ready for short-lived Site credential JSON on hidden stdin.',flush=True)
credential=json.loads(sys.stdin.readline())
manifest=json.loads((ROOT/'.openai/hosting.json').read_text())
env=os.environ.copy();env['GIT_TERMINAL_PROMPT']='0'
token=credential.get('token')
if token:
 count=int(env.get('GIT_CONFIG_COUNT','0'))
 env['GIT_CONFIG_COUNT']=str(count+1)
 env[f'GIT_CONFIG_KEY_{count}']='http.extraHeader'
 env[f'GIT_CONFIG_VALUE_{count}']='Authorization: Bearer '+token

def run(args,capture=False):
 proc=subprocess.run(args,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if proc.returncode:
  diagnostic=(proc.stdout+'\n'+proc.stderr)
  if token:diagnostic=diagnostic.replace(token,'[REDACTED]')
  raise RuntimeError('Command failed: '+str(args[0:2])+'\n'+diagnostic)
 if not capture and proc.stdout:print(proc.stdout.strip(),flush=True)
 return proc.stdout.strip()
try:
 remote=run(['git','remote','get-url','origin'],True)
 if remote!=credential['remote_url']:raise ValueError('Credential remote differs from retained Sites origin')
 branch=credential['branch']
 run(['git','fetch','origin',branch])
 run(['git','merge-base','--is-ancestor',f'origin/{branch}','HEAD'])
 run([sys.executable,'scripts/build.py'])
 run([sys.executable,'scripts/check.py'])
 run(['git','add','--all'])
 if run(['git','diff','--cached','--name-only'],True):
  run(['git','commit','-m',os.environ.get('SITE_RELEASE_MESSAGE','Keep research evidence, progress and website synchronized')])
 sha=run(['git','rev-parse','HEAD'],True)
 run(['git','push','origin',f'HEAD:{branch}'])
 remote_sha=run(['git','ls-remote','origin',f'refs/heads/{branch}'],True).split()[0]
 if remote_sha!=sha:raise RuntimeError('Pushed remote HEAD differs from local commit')
 if run(['git','status','--porcelain'],True):raise RuntimeError('Working tree changed after commit')
 target=ROOT/'artifacts'/f'sites-{sha}.tar.gz';target.parent.mkdir(exist_ok=True)
 with tarfile.open(target,'w:gz')as archive:
  archive.add(ROOT/'.openai/hosting.json',arcname='.openai/hosting.json')
  archive.add(ROOT/'dist',arcname='dist')
 print(json.dumps({'project_id':manifest['project_id'],'commit_sha':sha,'archive':str(target),'remote_verified':True,'native_publish_still_required':True}),flush=True)
except Exception as exc:
 print(str(exc),file=sys.stderr);sys.exit(1)
