"""Reproduce the lab metrics without modifying the generated solutions.

Each solution is copied into a temporary directory as ``bowling.py`` together
with the unchanged Exercism test file, because the tests import that module
name. The results of pytest, Radon and Pylint are stored in ``analysis/`` and
summarised in ``metrics.csv`` next to this script.
"""
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

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
OUT = ROOT / 'analysis'
TEST = ROOT / 'tests/bowling_test.py'
PROMPTS = ('P0', 'P1', 'P2')
MODEL = 'DeepSeek'
TEST_SUITE = 'Exercism Python Bowling (скачанный тестовый файл)'


def run(args, cwd):
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable, *args], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=120)


def blocks(items):
    for item in items:
        if item.get('type') in ('function', 'method'):
            yield item
        yield from blocks(item.get('methods', []))
        yield from blocks(item.get('closures', []))


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    results = []
    for prompt in PROMPTS:
        source = ROOT / 'answers' / prompt / 'bowling.py'
        source.read_text(encoding='utf-8')
        ast.parse(source.read_text(encoding='utf-8'), feature_version=(3, 11))
        with tempfile.TemporaryDirectory(prefix='bowling-lab5-') as directory:
            work = Path(directory)
            shutil.copyfile(source, work / 'bowling.py')
            shutil.copyfile(TEST, work / 'bowling_test.py')

            report = OUT / f'{prompt}_pytest.xml'
            proc = run(['-m', 'pytest', '-q', '-p', 'no:cacheprovider',
                        'bowling_test.py', f'--junitxml={report}', '--tb=short'], work)
            (OUT / f'{prompt}_pytest.txt').write_text(proc.stdout + proc.stderr)
            if proc.returncode not in (0, 1):
                raise RuntimeError(proc.stdout + proc.stderr)

            cases = []
            for case in ET.parse(report).findall('.//testcase'):
                issue = case.find('failure')
                if issue is None:
                    issue = case.find('error')
                cases.append({'test': case.get('name'),
                              'status': 'passed' if issue is None else 'failed'})
            failed = [case['test'] for case in cases if case['status'] == 'failed']

            radon = run(['-m', 'radon', 'cc', '-s', '-j', 'bowling.py'], work)
            if radon.returncode:
                raise RuntimeError(radon.stderr)
            (OUT / f'{prompt}_radon.json').write_text(radon.stdout)
            measures = list(blocks(json.loads(radon.stdout)['bowling.py']))
            hardest = max(measures, key=lambda item: item['complexity'])

            pylint = run(['-m', 'pylint', '--rcfile=/dev/null', '--persistent=n',
                          '--py-version=3.11', '--output-format=json2', 'bowling.py'], work)
            (OUT / f'{prompt}_pylint.json').write_text(pylint.stdout)
            lint = json.loads(pylint.stdout)
            raw_score = lint['statistics']['score']
            counts = {kind: sum(message['type'] == kind for message in lint['messages'])
                      for kind in ('error', 'warning', 'refactor', 'convention', 'fatal')}

            passed = sum(case['status'] == 'passed' for case in cases)
            results.append({
                'model': MODEL, 'prompt': prompt,
                'passed': passed, 'total': len(cases),
                'tpr': passed / len(cases) * 100,
                'failed_tests': failed,
                'cc_max': hardest['complexity'], 'cc_method': hardest['name'],
                'pylint_raw': raw_score, 'pylint_score': max(0.0, raw_score),
                **counts,
                'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'syntax_python311': True, 'cases': cases,
            })
            print(prompt, f'{passed}/{len(cases)}', 'CC', hardest['complexity'],
                  'Pylint', round(raw_score, 2), flush=True)

    (OUT / 'results.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

    with (ROOT / 'metrics.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['prompt', 'passed', 'total', 'tpr_percent', 'tests_status',
                         'cc_max', 'pylint_score', 'source_sha256', 'test_sha256',
                         'python', 'test_suite'])
        for result in results:
            writer.writerow([
                result['prompt'], result['passed'], result['total'],
                f"{result['tpr']:.1f}", 'OK' if not result['failed_tests'] else 'FAILED',
                result['cc_max'], f"{result['pylint_score']:.2f}", result['sha256'],
                hashlib.sha256(TEST.read_bytes()).hexdigest(),
                platform.python_version(), TEST_SUITE,
            ])

    versions = {name: importlib.metadata.version(name) for name in ('pytest', 'radon', 'pylint')}
    (ROOT / 'requirements.txt').write_text(
        ''.join(f'{name}=={version}\n' for name, version in versions.items()), encoding='utf-8')
    environment = {
        'python': platform.python_version(), 'platform': platform.platform(),
        'tools': versions, 'model': MODEL,
        'test_sha256': hashlib.sha256(TEST.read_bytes()).hexdigest(),
        'test_count': len(results[0]['cases']),
        'target_python': '3.11',
        'pylint_config': 'default; rcfile=/dev/null; persistent=n; py-version=3.11',
        'cc_definition': 'maximum of Radon function/method complexity, class aggregate excluded',
    }
    (OUT / 'environment.json').write_text(
        json.dumps(environment, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
