"""Exploratory checks; these do not affect the fixed 31-test TPR."""
from pathlib import Path
import importlib.util
import json

root = Path(__file__).resolve().parent
records = []
for model in ('deepseek', 'alice', 'qwen'):
    for prompt in ('P0', 'P1', 'P2'):
        spec = importlib.util.spec_from_file_location('candidate', root / 'answers' / model / prompt / 'bowling.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        row = {'model': model, 'prompt': prompt}
        for name, value in [('bool', True), ('fraction', 1.5)]:
            game = module.BowlingGame()
            try:
                game.roll(value)
                row[name] = 'accepted'
            except Exception as exc:
                row[name] = f'{type(exc).__name__}: {exc}'
        game = module.BowlingGame()
        try:
            game.score()
            row['empty_score'] = 'accepted'
        except Exception as exc:
            row['empty_score'] = f'{type(exc).__name__}: {exc}'
        game = module.BowlingGame()
        try:
            game.roll(5)
            try:
                game.roll(6)
                row['recovery'] = 'invalid roll accepted'
            except Exception as exc:
                row['rejection'] = f'{type(exc).__name__}: {exc}'
                game.roll(5)
                for _ in range(18):
                    game.roll(0)
                row['recovery'] = f'score={game.score()} (expected 10)'
        except Exception as exc:
            row['recovery'] = f'{type(exc).__name__}: {exc}'
        records.append(row)
(root / 'analysis/supplementary.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
for row in records:
    print(row)
