"""Extra checks that are not part of the 31-test suite.

The official tests only require *some* exception for invalid input. These
checks look at the properties the exam question describes in prose: strict
integer interface, and state that is not damaged by a rejected delivery.
They are reported separately and do not change TPR.
"""
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
OUT = ROOT / 'analysis' / 'supplementary.json'


def load(prompt):
    spec = importlib.util.spec_from_file_location(f'bowling_{prompt}',
                                                  ROOT / 'answers' / prompt / 'bowling.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.BowlingGame


def check(game_class, value):
    game = game_class()
    try:
        game.roll(value)
    except Exception as error:  # noqa: BLE001 - the type is part of the report
        return {'accepted': False, 'exception': type(error).__name__}
    return {'accepted': True, 'exception': None}


def resume_after_rejection(game_class):
    game = game_class()
    game.roll(5)
    rejected = False
    try:
        game.roll(6)
    except Exception:  # noqa: BLE001 - the fact of rejection is the point
        rejected = True
    if not rejected:
        return {'rejected': False, 'score': None}
    game.roll(5)
    for _ in range(18):
        game.roll(0)
    try:
        return {'rejected': True, 'score': game.score()}
    except Exception as error:  # noqa: BLE001
        return {'rejected': True, 'score': None, 'exception': type(error).__name__}


def main():
    report = {}
    for prompt in ('P0', 'P1', 'P2'):
        game_class = load(prompt)
        report[prompt] = {
            'roll_true': check(game_class, True),
            'roll_float': check(game_class, 1.5),
            'roll_str': check(game_class, '3'),
            'resume_after_rejection': resume_after_rejection(game_class),
        }
        print(prompt, report[prompt], flush=True)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    sys.exit(main())
