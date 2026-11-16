#!/usr/bin/env python3
"""Build the public static site from one reviewed repository, using only Python stdlib."""
from __future__ import annotations
import argparse,csv,hashlib,html,json,re,shutil,sys,zipfile
from pathlib import Path

def escape(value):
 return html.escape(str(value),quote=True)
def digest(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
def jstext(value):
 return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
def task_label(task):
 return task.get('title') or task.get('name') or task.get('topic') or task.get('id','未命名任务')
def generate(root:Path,output:Path):
 root=root.resolve();output=output.resolve()
 if output==root or root.is_relative_to(output) or (output.is_relative_to(root) and output!=root/'dist'):
  raise ValueError('构建输出不能是项目根目录或它的父目录')
 param=root/'research/data/qingyuan_public_parameters.json';pricesfile=root/'research/data/economics_spot_20261115_96points.csv'
 progressfile=root/'research/progress.json';stationsfile=root/'research/data/stations_2023.json'
 for p in [param,pricesfile,progressfile,stationsfile,root/'README.md',root/'LICENSE']:
  if not p.is_file():raise ValueError(f'构建缺少必要输入：{p.relative_to(root)}')
 data=json.loads(param.read_text());progress=json.loads(progressfile.read_text());stations=json.loads(stationsfile.read_text())
 with pricesfile.open(encoding='utf-8-sig',newline='') as f:prices=list(csv.DictReader(f))
 if not prices:raise ValueError('电价CSV不能为空')
 # This is an explicitly generated source index; the dataset's sources remain authoritative.
 sourceindex=root/'research/sources/index.json';sourceindex.parent.mkdir(exist_ok=True,parents=True)
 sourceindex.write_text(json.dumps({'generated_from':'research/data/qingyuan_public_parameters.json#/sources','retrieved_at':data['metadata'].get('retrieved_at'),'sources':data['sources']},ensure_ascii=False,indent=2)+'\n')
 if output.exists():shutil.rmtree(output)
 shutil.copytree(root/'site',output)
 (output/'data').mkdir(exist_ok=True)
 for p in (root/'research/data').iterdir():
  if p.is_file():shutil.copy2(p,output/'data'/p.name)
 shutil.copy2(stationsfile,output/'stations.json')
 (output/'data/progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
 shutil.copy2(sourceindex,output/'data/sources.json')
 for name in ['README.md','LICENSE']:shutil.copy2(root/name,output/name)
 (output/'station-data.js').write_text('const stationRecords='+jstext(stations)+';\n')
 (output/'research-data.js').write_text('const researchPrices='+jstext(prices)+';\nconst researchProgress='+jstext(progress)+';\n')
 taskdata=progress.get('tasks',[]);status_names={'todo':'待研究','in_progress':'进行中','blocked':'等待数据或连接','done':'已完成','verified':'已核验'}
 rows=''.join('<tr>'+''.join('<td>'+escape(x)+'</td>'for x in [p['parameter'],p['value'],p['unit'],p['status'],p['source_ids'],p.get('notes','')])+'</tr>'for p in data['parameters'])
 gaps=''.join('<details><summary>'+escape(g[0]+' · '+g[1])+'</summary><p>用途：'+escape(g[2])+'。资料状态：'+escape(g[3])+'。</p><p>'+escape(g[4])+'</p></details>'for g in data['missing_parameters'])
 sourcelinks=''.join('<a href="'+escape(s[4])+'" target="_blank" rel="noopener">'+escape(s[0]+' · '+s[2])+'<small>'+escape(s[1]+' · '+s[3]+' · '+s[5])+'</small></a>'for s in data['sources'])
 tasks=''
 for task in taskdata:
  status=task.get('status','todo');accept=task.get('acceptance',[])
  if isinstance(accept,str):accept=[accept]
  limitations=task.get('limitations') or task.get('blocked_reason') or task.get('blockers','')
  if isinstance(limitations,list):limitations='；'.join(str(x)for x in limitations)
  tasks+='<article class="research-task" data-task-id="'+escape(task.get('id',''))+'"><p class="task-state">'+escape(task.get('id','')+' · '+status_names.get(status,status))+'</p><h3>'+escape(task_label(task))+'</h3>'
  if task.get('description'):tasks+='<p>'+escape(task['description'])+'</p>'
  if task.get('gap_ids'):tasks+='<p>关联缺口：'+escape('、'.join(task['gap_ids']))+'</p>'
  if accept:tasks+='<p>验收要求：'+escape('；'.join(accept))+'</p>'
  if limitations:tasks+='<p>限制：'+escape(limitations)+'</p>'
  tasks+='</article>'
 done=sum(t.get('status')=='done'for t in taskdata)
 sync=progress.get('sync',{})
 if not isinstance(sync,dict):sync={}
 syncparts=['研究数据、来源、缺口和任务在同一仓库中维护，运行构建后生成本页与下载包。']
 for k,label in [('github_status','GitHub'),('publication_status','原站发布'),('sites_status','Sites'),('automatic_github_to_sites_sync','GitHub至Sites自动同步'),('domestic_status','中国大陆访问'),('deployment_note','发布说明')]:
  value=sync.get(k)
  if value:
   display={'awaiting_account_connection':'等待账号连接','pending':'等待本次发布','not_configured':'尚未配置','published':'已发布','succeeded':'已成功','blocked':'受阻','verified':'已核验','publishing':'正在发布','passed':'检查通过','three_mainland_probes_http_403':'三地三运营商探针HTTP403'}.get(str(value),str(value))
   syncparts.append(label+'：'+display)
 github_url=sync.get('github_url')
 if github_url:syncparts.append('公开仓库：'+str(github_url))
 replacements={'PARAMETER_ROWS':rows,'GAP_ITEMS':gaps,'SOURCE_LINKS':sourcelinks,'TASK_CARDS':tasks,'PARAMETER_COUNT':str(len(data['parameters'])),'PRICE_COUNT':str(len(prices)),'GAP_COUNT':str(len(data['missing_parameters'])),'TASK_COUNT':str(len(taskdata)),'DONE_COUNT':str(done),'UPDATED_AT':escape(progress.get('updated_at',data['metadata'].get('retrieved_at',''))),'PRICE_DATE':escape(prices[0]['date']),'PRICE_START':escape(prices[0]['interval_end_Asia_Shanghai']),'PRICE_END':escape(prices[-1]['interval_end_Asia_Shanghai']),'SYNC_NOTE':escape(' '.join(syncparts))}
 page=(root/'site/research.html').read_text()
 for key,value in replacements.items():page=page.replace('{{'+key+'}}',value)
 if re.search(r'\{\{[A-Z_]+\}\}',page):raise ValueError('研究页存在未解析模板标记')
 (output/'research.html').write_text(page)
 # Source archive deliberately excludes build output, Git metadata, credentials, PDFs and nested ZIPs.
 archive=output/'downloads/pumped-storage-source.zip';archive.parent.mkdir(exist_ok=True)
 files=[]
 for name in ['site','scripts','research','docs','.github']:
  folder=root/name
  if folder.exists():files.extend(f for f in folder.rglob('*')if f.is_file())
 files.extend(p for p in [root/'README.md',root/'LICENSE',root/'AGENTS.md',root/'.gitignore',root/'.openai/hosting.json']if p.is_file())
 def exportable(p):
  rel=p.relative_to(root)
  return not any(x in {'.git','__pycache__','node_modules','local-status','artifacts'}for x in rel.parts)and p.suffix.lower()not in {'.pdf','.zip','.pyc'}and not p.name.startswith('.env')
 files=sorted(set(f for f in files if exportable(f)),key=lambda p:p.relative_to(root).as_posix())
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in files:
   info=zipfile.ZipInfo(p.relative_to(root).as_posix(),date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,p.read_bytes())
 manifest={'schema_version':1,'project':'qingyuan-hydro-thesis','canonical_inputs':{str(p.relative_to(root)):digest(p)for p in [param,pricesfile,stationsfile,progressfile]},'parameter_count':len(data['parameters']),'price_count':len(prices),'gap_count':len(data['missing_parameters']),'task_count':len(taskdata),'source_bundle_sha256':digest(archive),'source_files':[{'path':p.relative_to(root).as_posix(),'sha256':digest(p)}for p in files],'outputs':{p.relative_to(output).as_posix():digest(p)for p in sorted(output.rglob('*'))if p.is_file()}}
 (output/'sync-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 return {'output':str(output),'parameters':len(data['parameters']),'price_points':len(prices),'tasks':len(taskdata),'source_files':len(files),'source_zip_bytes':archive.stat().st_size}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output',type=Path);args=ap.parse_args()
 try:print(json.dumps(generate(args.root,args.output or args.root/'dist'),ensure_ascii=False))
 except (ValueError,KeyError,TypeError,OSError)as exc:print('构建失败：'+str(exc),file=sys.stderr);sys.exit(1)
if __name__=='__main__':main()
