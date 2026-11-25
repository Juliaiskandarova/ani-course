from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import ast,csv,importlib.metadata as md,json,os,subprocess,sys
import xml.etree.ElementTree as ET

base=Path(__file__).resolve().parent
test=base/'tests/bowling_test.py'
analysis=base/'analysis'
analysis.mkdir(exist_ok=True)
test_ast=ast.parse(test.read_text(encoding='utf-8'))
count=sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(test_ast))
assert count==31
environment={'python':sys.version.split()[0],
             **{k:md.version(k) for k in ('pytest','radon','pylint')},
             'test_sha256':sha256(test.read_bytes()).hexdigest(),
             'suite_size':count}
(analysis/'environment.json').write_text(json.dumps(environment,indent=2)+'\n',encoding='utf-8')

def execute(folder, *args):
    env=dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONIOENCODING='utf-8',
             PYTHONDONTWRITEBYTECODE='1', NO_COLOR='1')
    pkg = env.get('PYTHONPATH','')
    env['PYTHONPATH']=str(folder)+(os.pathsep+pkg if pkg else '')
    p=subprocess.run([sys.executable,'-B','-m',*args],cwd=folder,env=env,capture_output=True,
                     encoding='utf-8',errors='replace',timeout=60)
    return p

def blocks(blocks_list):
    for c in blocks_list:
        if c['type'] == 'class':
            yield from blocks(c['methods'])
        else:
            yield c

def run(folder):
    label=folder.name
    directory=analysis/label
    directory.mkdir(exist_ok=True)
    xml=directory/'pytest.xml'
    checks=execute(folder,'pytest','-q','--tb=short','--import-mode=importlib',
                   '-p','no:cacheprovider',f'--junitxml={xml}',str(test))
    (directory/'pytest.txt').write_text((checks.stdout+checks.stderr).replace(str(base),'.'),encoding='utf-8')
    root=ET.parse(xml)
    cases=list(root.iter('testcase'))
    assert len(cases)==count, (label,len(cases))
    fails=[]
    for case in cases:
        for field in ('failure','error','skipped'):
            e=case.find(field)
            if e is not None:
                fails.append((label,case.get('name'),field,(e.get('message') or '').replace(str(base),'.')))
                break
    xml.write_text(xml.read_text(encoding='utf-8').replace(str(base),'.'),encoding='utf-8')

    c=execute(folder,'radon','cc','-j','bowling.py')
    assert c.returncode==0
    (directory/'radon.json').write_text(c.stdout,encoding='utf-8')
    radon=json.loads(c.stdout)['bowling.py']
    hardest=max(blocks(radon),key=lambda node:node['complexity'])

    l=execute(folder,'pylint','bowling.py','--output-format=json2','--reports=no','--score=y')
    lint=json.loads(l.stdout)
    score=lint['statistics']['score']
    (directory/'pylint.json').write_text(l.stdout.replace(str(base),'.'),encoding='utf-8')
    vals=[label,count-len(fails),count,f'{100*(count-len(fails))/count:.2f}',
          hardest['complexity'],hardest['name'],f'{score:.2f}']
    return vals,fails

dirs=sorted(p for p in (base/'code').iterdir() if (p/'bowling.py').is_file())
assert len(dirs)==9
with ThreadPoolExecutor(3) as pool:
    results=list(pool.map(run,dirs))
for name,header,rows in [
    ('metrics.csv',['вариант','пройдено','всего','TPR (%)','CC max','метод','Pylint'],[r for r,_ in results]),
    ('failures.csv',['вариант','тест','статус','сообщение'],[f for _,rows in results for f in rows]),
]:
    with (analysis/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';')
        writer.writerow(header)
        writer.writerows(rows)
print(environment)
for r,f in results:
    print(r)
    for row in f:
        print(row)
