"""Reproduce the lab metrics without modifying generated solutions."""
from pathlib import Path
import ast
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'analysis'


def run(args, cwd):
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable, *args], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=60)


def blocks(items):
    for item in items:
        if item.get('type') in ('function', 'method'):
            yield item
        yield from blocks(item.get('methods', []))
        yield from blocks(item.get('closures', []))


def main():
    OUT.mkdir(exist_ok=True)
    test = ROOT / 'tests/bowling_test.py'
    results = []
    failures = []
    for model in ('deepseek', 'alice', 'qwen'):
        for prompt in ('P0', 'P1', 'P2'):
            source = ROOT / 'answers' / model / prompt / 'bowling.py'
            if not source.exists():
                continue
            prefix = f'{model}_{prompt}'
            ast.parse(source.read_text(), feature_version=(3, 11))
            with tempfile.TemporaryDirectory(prefix='bowling-lab5-') as directory:
                work = Path(directory)
                shutil.copyfile(source, work / 'bowling.py')
                shutil.copyfile(test, work / 'bowling_test.py')
                report = OUT / f'{prefix}_pytest.xml'
                proc = run(['-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                            'bowling_test.py', f'--junitxml={report}', '--tb=short'], work)
                (OUT / f'{prefix}_pytest.txt').write_text(proc.stdout + proc.stderr)
                if proc.returncode not in (0, 1):
                    raise RuntimeError(proc.stdout + proc.stderr)
                cases = []
                for case in ET.parse(report).findall('.//testcase'):
                    issue = case.find('failure')
                    if issue is None:
                        issue = case.find('error')
                    status = 'passed' if issue is None else 'failed'
                    entry = {'test': case.get('name'), 'status': status}
                    if issue is not None:
                        entry['traceback'] = issue.text
                        failures.append({'model': model, 'prompt': prompt,
                                         'test': case.get('name'), 'message': issue.get('message'),
                                         'traceback': issue.text})
                    cases.append(entry)
                radon = run(['-m', 'radon', 'cc', '-s', '-j', 'bowling.py'], work)
                if radon.returncode:
                    raise RuntimeError(radon.stderr)
                (OUT / f'{prefix}_radon.json').write_text(radon.stdout)
                measures = list(blocks(json.loads(radon.stdout)['bowling.py']))
                most_complex = max(measures, key=lambda item: item['complexity'])
                pylint = run(['-m', 'pylint', '--rcfile=/dev/null', '--persistent=n',
                              '--py-version=3.11', '--output-format=json2', 'bowling.py'], work)
                (OUT / f'{prefix}_pylint.json').write_text(pylint.stdout)
                lint = json.loads(pylint.stdout)
                score = lint['statistics']['score']
                counts = {key: sum(m['type'] == key for m in lint['messages'])
                          for key in ('error', 'warning', 'refactor', 'convention', 'fatal')}
                passed = sum(case['status'] == 'passed' for case in cases)
                result = {'model': model, 'prompt': prompt, 'passed': passed,
                          'total': len(cases), 'tpr': passed / len(cases) * 100,
                          'cc_max': most_complex['complexity'], 'cc_method': most_complex['name'],
                          'pylint_raw': score, 'pylint_score': max(0, score), **counts,
                          'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                          'syntax_python311': True, 'cases': cases}
                results.append(result)
                print(prefix, f'{passed}/{len(cases)}', 'CC', result['cc_max'],
                      'Pylint', round(score, 2), flush=True)
    (OUT / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
    fields = [key for key in results[0] if key != 'cases']
    with (OUT / 'metrics.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=';')
        writer.writeheader()
        writer.writerows({key: value for key, value in row.items() if key != 'cases'} for row in results)
    with (OUT / 'failures.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['model', 'prompt', 'test', 'message', 'traceback'], delimiter=';')
        writer.writeheader()
        writer.writerows(failures)
    versions = {name: importlib.metadata.version(name) for name in ('pytest', 'radon', 'pylint')}
    (ROOT / 'requirements.txt').write_text(''.join(f'{name}=={version}\n' for name, version in versions.items()))
    environment = {'python': platform.python_version(), 'platform': platform.platform(),
                   'tools': versions, 'test_sha256': hashlib.sha256(test.read_bytes()).hexdigest(),
                   'test_count': 31, 'date': '2026-11-23', 'pylint_config': 'default; rcfile=/dev/null; py-version=3.11',
                   'cc_definition': 'maximum of Radon function/method complexity, excluding class aggregate',
                   'pylint_score_definition': 'max(0, actual Pylint score); raw score also retained'}
    (OUT / 'environment.json').write_text(json.dumps(environment, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
