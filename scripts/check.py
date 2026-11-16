#!/usr/bin/env python3
"""Verify research evidence integrity, static delivery and one-change propagation."""
from __future__ import annotations
import argparse,csv,html,json,math,re,shutil,subprocess,sys,tempfile,hashlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
from zipfile import ZipFile

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.links=[];self.ids=set();self.parameter_rows=0;self.param_depth=0;self.in_script=0;self.text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for attr in ('href','src'):
            if a.get(attr):self.links.append(a[attr])
        if tag=='tbody' and a.get('id')=='parameter-rows':self.param_depth+=1
        elif tag=='tbody' and self.param_depth:self.param_depth+=1
        if tag=='tr' and self.param_depth:self.parameter_rows+=1
        if tag in ('script','style'):self.in_script+=1
    def handle_endtag(self,tag):
        if tag=='tbody' and self.param_depth:self.param_depth-=1
        if tag in ('script','style') and self.in_script:self.in_script-=1
    def handle_data(self,data):
        if not self.in_script:self.text.append(data)

def require(value,message):
    if not value:raise AssertionError(message)

def read_price(path):
    with path.open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))

def text_page(path):
    p=Page();p.feed(path.read_text(encoding='utf-8'));return p

def validate(root,out):
    data_path=root/'research/data/qingyuan_public_parameters.json';data=json.loads(data_path.read_text())
    params=data['parameters'];keys=[x['key']for x in params]
    require(len(keys)==len(set(keys)),'duplicate parameter key')
    sources={x[0] if isinstance(x,list) else x['id'] for x in data['sources']}
    for item in params:
        require(set(item['source_ids'].split(';'))<=sources,'unresolved source for '+item['key'])
    p={x['key']:x['value']for x in params}
    for level in ('upper','lower'):
        require(p[level+'_normal_level_m']>p[level+'_dead_level_m'],level+' water level order')
        require(p[level+'_total_storage_m3']>=p[level+'_normal_storage_m3']>=p[level+'_regulating_storage_m3']>0,level+' storage order')
    require(json.loads((out/'data/qingyuan_public_parameters.json').read_text())==data,'website JSON differs from canonical research JSON')
    price_name='economics_spot_20261115_96points.csv';prices=read_price(root/'research/data'/price_name)
    require(prices,'empty price sample')
    require(len({(r['date'],r['interval_end_Asia_Shanghai'])for r in prices})==len(prices),'duplicate price intervals')
    for row in prices:
        for kind in ('day_ahead','real_time'):
            a=float(row[kind+'_CNY_per_MWh']);b=float(row[kind+'_CNY_per_kWh'])
            require(math.isfinite(a)and math.isfinite(b),'non-finite electricity price')
            require(math.isclose(a/1000,b,abs_tol=1e-10),'MWh/kWh conversion error')
    require(data.get('price_data')==prices,'parameter JSON price snapshot differs from canonical price CSV; update both together')
    with (root/'research/data/qingyuan_public_parameters.csv').open(encoding='utf-8-sig',newline='')as f:
        parameter_csv=list(csv.DictReader(f))
    require(len(parameter_csv)==len(params),'parameter CSV row count differs from JSON')
    for original,download in zip(params,parameter_csv):
        require(all(str(original.get(k,''))==download.get(k,'') for k in original),'parameter CSV differs from JSON for '+original['key'])
    require(json.loads((root/'research/sources/index.json').read_text())['sources']==data['sources'],'generated source index differs from authoritative sources')
    require(json.loads((out/'data/sources.json').read_text())['sources']==data['sources'],'website source index is stale')
    station_js=(out/'station-data.js').read_text().strip()
    require(station_js.startswith('const stationRecords=')and station_js.endswith(';'),'station data script format')
    require(json.loads(station_js[len('const stationRecords='):-1])==json.loads((root/'research/data/stations_2023.json').read_text()),'station data script differs from canonical JSON')
    delivered_prices=read_price(out/'data'/price_name)
    require(delivered_prices==prices,'delivered price sequence changed; preserve negative prices')
    negative=sum(float(x['real_time_CNY_per_MWh'])<0 for x in prices)
    research_page=text_page(out/'research.html')
    require(research_page.parameter_rows==len(params),f'parameter HTML rows {research_page.parameter_rows} != {len(params)}')
    visible=' '.join(research_page.text)
    for item in params:
        require(item['parameter'] in visible,'parameter omitted from HTML: '+item['key'])
    for gap in data['missing_parameters']:
        gap_id=gap[0]if isinstance(gap,list)else gap['id']
        require(gap_id in visible,'missing research gap omitted from website: '+gap_id)
    checked_links=0
    for file in out.rglob('*.html'):
        page=text_page(file)
        for link in page.links:
            url=urlsplit(link)
            if url.scheme or url.netloc or not url.path:continue
            decoded=unquote(url.path)
            target=out/decoded.lstrip('/')if decoded.startswith('/')else file.parent/decoded
            if target.is_dir():target=target/'index.html'
            if not target.exists() and not target.suffix and target.with_suffix('.html').exists():target=target.with_suffix('.html')
            require(target.resolve().is_relative_to(out.resolve()),'local link escapes output: '+link)
            require(target.exists(),f'broken local link: {file.relative_to(out)} -> {link}')
            checked_links+=1
    node=shutil.which('node');require(node,'Node.js needed to validate JavaScript')
    js=list(out.rglob('*.js'))
    for script in js:
        run=subprocess.run([node,'--check',str(script)],capture_output=True,text=True)
        require(run.returncode==0,'JavaScript syntax error: '+str(script.relative_to(out))+' '+run.stderr[:300])
    archive=out/'downloads/pumped-storage-source.zip'
    with ZipFile(archive)as z:
        names=set(z.namelist())
        for name in names:
            path=Path(name)
            require(not path.is_absolute()and '..'not in path.parts,'unsafe path in source ZIP')
            require(not any(part in ('.git','dist','node_modules','__pycache__')for part in path.parts),'generated/private directory in source ZIP: '+name)
            require(not path.name.startswith('.env'),'environment secret file in ZIP: '+name)
            require(path.suffix.lower()not in ('.pdf','.zip','.pyc'),'third-party PDF/recursive ZIP/bytecode in source ZIP: '+name)
        for needed in ('README.md','LICENSE','scripts/build.py','research/data/qingyuan_public_parameters.json'):
            require(needed in names,'source ZIP missing '+needed)
        require(z.read('research/data/qingyuan_public_parameters.json')==data_path.read_bytes(),'ZIP data differs from canonical data')
    manifest=json.loads((out/'sync-manifest.json').read_text())
    for path,expected in manifest['outputs'].items():
        require(hashlib.sha256((out/path).read_bytes()).hexdigest()==expected,'output hash differs from sync manifest: '+path)
    for path,expected in manifest['canonical_inputs'].items():
        require(hashlib.sha256((root/path).read_bytes()).hexdigest()==expected,'canonical input changed after build: '+path)
    progress=json.loads((root/'research/progress.json').read_text())
    return {'parameters':len(params),'sources':len(sources),'price_points':len(prices),'negative_real_time_points':negative,'missing_groups':len(data['missing_parameters']),'javascript_files':len(js),'checked_local_links':checked_links,'tasks':len(progress.get('tasks',[]))}

def regression(root):
    # Changing a canonical parameter and research task must change visible site content.
    # This catches stale embedded HTML/JS even when all files are individually well formed.
    with tempfile.TemporaryDirectory(prefix='qingyuan-sync-')as td:
        project=Path(td)/'project';project.mkdir()
        for name in ('site','research','docs','.github','.openai','scripts'):
            if (root/name).exists():shutil.copytree(root/name,project/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for name in ('README.md','LICENSE','.gitignore'):
            if (root/name).exists():shutil.copy2(root/name,project/name)
        p=project/'research/data/qingyuan_public_parameters.json';data=json.loads(p.read_text())
        marker=987654321.125;data['parameters'][0]['value']=marker;p.write_text(json.dumps(data,ensure_ascii=False,indent=2))
        q=project/'research/progress.json';progress=json.loads(q.read_text());tasks=progress.get('tasks',[])
        require(tasks,'need at least one tracked task for synchronization regression')
        title='同步回归标记：修改研究任务后页面必须更新';tasks[0]['title']=title;q.write_text(json.dumps(progress,ensure_ascii=False,indent=2))
        output=project/'dist'
        result=subprocess.run([sys.executable,str(project/'scripts/build.py'),'--root',str(project),'--output',str(output)],capture_output=True,text=True)
        require(result.returncode==0,'isolated synchronization build failed: '+result.stdout[-400:]+result.stderr[-400:])
        visible=' '.join(text_page(output/'research.html').text)
        require(str(marker)in visible,'canonical parameter update failed to reach visible HTML')
        require(title in visible,'research task update failed to reach visible HTML')
        require(json.loads((output/'data/qingyuan_public_parameters.json').read_text())==data,'changed research JSON failed to propagate to download')
    return 'passed'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output',type=Path);ap.add_argument('--skip-sync-test',action='store_true');args=ap.parse_args()
    root=args.root.resolve();out=(args.output or root/'dist').resolve()
    try:
        result=validate(root,out)
        result['synchronization_regression']='skipped'if args.skip_sync_test else regression(root)
        print(json.dumps({'status':'passed',**result},ensure_ascii=False))
    except (AssertionError,ValueError,KeyError,OSError)as exc:
        print(json.dumps({'status':'failed','error':str(exc)},ensure_ascii=False));return 1
    return 0
if __name__=='__main__':sys.exit(main())
