#!/usr/bin/env python3
"""Check Pages readiness without trying to create or change the site's settings."""
from pathlib import Path
import json,os,sys,urllib.error,urllib.request
repo=os.environ.get('GITHUB_REPOSITORY','')
if len(repo.split('/'))!=2 or not all(repo.split('/')):
 raise SystemExit('GITHUB_REPOSITORY must be owner/repository')
api=os.environ.get('GITHUB_API_URL','https://api.github.com').rstrip('/')
headers={'Accept':'application/vnd.github+json','User-Agent':'qingyuan-pages-readiness'}
token=os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
if token:headers['Authorization']='Bearer '+token
settings='https://github.com/'+repo+'/settings/pages'
try:
 with urllib.request.urlopen(urllib.request.Request(api+'/repos/'+repo+'/pages',headers=headers),timeout=30) as response:
  data=json.load(response)
 enabled=data.get('build_type')=='workflow'
 status='ready' if enabled else 'select_github_actions_source'
 url=data.get('html_url','') if enabled else ''
except urllib.error.HTTPError as error:
 if error.code!=404:
  print('Pages configuration check failed: HTTP '+str(error.code),file=sys.stderr)
  raise SystemExit(1)
 enabled=False;status='pages_not_configured_or_not_visible';url=''
message='Pages已准备好，继续部署。' if enabled else 'Pages尚未配置为GitHub Actions；本次检查和构建已完成，但未发布Pages。请打开 '+settings+' 选择 GitHub Actions，再重新运行工作流。'
print(json.dumps({'enabled':enabled,'status':status,'settings_url':settings,'page_url':url,'message':message},ensure_ascii=False))
output=os.environ.get('GITHUB_OUTPUT')
if output:
 with open(output,'a',encoding='utf-8')as stream:
  stream.write('enabled='+str(enabled).lower()+'\nstatus='+status+'\npage_url='+url.replace('\n','')+'\n')
summary=os.environ.get('GITHUB_STEP_SUMMARY')
if summary:
 with open(summary,'a',encoding='utf-8')as stream:stream.write('## GitHub Pages\n\n'+message+'\n')
if not enabled:print('::notice title=Pages等待一次性设置::'+message)
