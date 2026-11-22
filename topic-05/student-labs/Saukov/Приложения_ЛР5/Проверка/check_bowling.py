"""Run the same Bowling checks against all nine saved answers."""

import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from importlib.metadata import version


HERE = Path(__file__).resolve().parent
TEST_FILE = HERE / "bowling_test.py"
ANSWERS = HERE.parent / "answers"


def run(directory, module, *args):
    environment = os.environ.copy()
    environment.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONUTF8="1")
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=directory,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )


def measure(answer, directory):
    shutil.copyfile(answer, directory / "bowling.py")
    shutil.copyfile(TEST_FILE, directory / TEST_FILE.name)
    tests = run(
        directory, "pytest", "-q", "--tb=short", "--color=no",
        "--junitxml=pytest.xml", TEST_FILE.name,
    )
    if tests.returncode not in (0, 1):
        raise RuntimeError(f"{answer.name}: pytest\n{tests.stdout}{tests.stderr}")
    cases = ET.parse(directory / "pytest.xml").findall(".//testcase")
    if len(cases) != 31:
        raise RuntimeError(f"{answer.name}: expected 31 tests, got {len(cases)}")
    failures = []
    for case in cases:
        failure = case.find("failure")
        if failure is not None:
            failures.append({
                "test": case.attrib["name"],
                "message": failure.attrib["message"],
            })
        elif case.find("skipped") is not None or case.find("error") is not None:
            raise RuntimeError(f"{answer.name}: unexpected test status")

    radon = run(directory, "radon", "cc", "-s", "-a", "-j", "bowling.py")
    radon.check_returncode()
    blocks = json.loads(radon.stdout)["bowling.py"]
    functions = [block for block in blocks if block["type"] in ("method", "function")]
    maximum = max(block["complexity"] for block in functions)
    most_complex = ", ".join(
        block["name"] for block in functions if block["complexity"] == maximum
    )

    pylint = run(directory, "pylint", "--output-format=json2", "bowling.py")
    if pylint.returncode & 32:
        raise RuntimeError(f"{answer.name}: pylint\n{pylint.stdout}{pylint.stderr}")
    lint = json.loads(pylint.stdout)
    counts = Counter(message["type"] for message in lint["messages"])
    passed = len(cases) - len(failures)
    model, prompt = answer.stem.rsplit("_", 1)
    metrics = {
        "Модель": model,
        "Промпт": prompt,
        "Пройдено": passed,
        "Всего": len(cases),
        "TPR, %": f"{100 * passed / len(cases):.2f}".replace(".", ","),
        "CC max": maximum,
        "Метод с CC max": most_complex,
        "Pylint Score": f"{lint['statistics']['score']:.2f}".replace(".", ","),
        "E": counts["error"],
        "W": counts["warning"],
        "R": counts["refactor"],
        "C": counts["convention"],
    }
    log = {
        "file": answer.name,
        "source_sha256": hashlib.sha256(answer.read_bytes()).hexdigest(),
        "failures": failures,
        "pytest": tests.stdout,
        "radon": blocks,
        "pylint": lint,
    }
    return metrics, log


def main():
    answers = sorted(ANSWERS.glob("*.py"))
    if len(answers) != 9:
        raise RuntimeError(f"Expected nine answers, got {len(answers)}")
    metrics = []
    logs = []
    with tempfile.TemporaryDirectory(prefix="lab5-bowling-") as temp:
        for answer in answers:
            directory = Path(temp) / answer.stem
            directory.mkdir()
            metric, log = measure(answer, directory)
            metrics.append(metric)
            logs.append(log)
            print(f"{answer.name}: {metric['Пройдено']}/{metric['Всего']}", flush=True)
    with (HERE / "Метрики.csv").open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(metrics[0]), delimiter=";")
        writer.writeheader()
        writer.writerows(metrics)
    data = {
        "python": sys.version.split()[0],
        "tools": {tool: version(tool) for tool in ("pytest", "radon", "pylint", "astroid")},
        "test_sha256": hashlib.sha256(TEST_FILE.read_bytes()).hexdigest(),
        "runs": logs,
    }
    (HERE / "Протокол.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
