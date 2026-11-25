from pathlib import Path
from collections import Counter
import csv
import math
import re

ROOT = Path(__file__).resolve().parent
RUNS = [(model, prompt) for model in ('glm', 'chatgpt', 'deepseek')
        for prompt in ('P1', 'P2')]
LABEL = r'(?:(?:part|часть)\s+)?[\[(]?\s*{}\s*[\])]?\s*[:.\-–—]?'
LABEL_A = re.compile(LABEL.format('[AА]'), re.I)
LABEL_B = re.compile(LABEL.format('[BБВ]'), re.I)


def clean(line):
    return re.sub(r'\*\*|__', '', line.strip()).strip('#*\x60 ').strip()


def part_a(raw):
    lines = raw.splitlines()
    markers = [index for index, line in enumerate(lines)
               if LABEL_B.fullmatch(clean(line))]
    if len(markers) != 1:
        raise ValueError('Не найдена одна отдельная метка [B]. Сохрани часть A отдельно.')
    stop = markers[0]
    starts = [index for index, line in enumerate(lines[:stop])
              if LABEL_A.fullmatch(clean(line))]
    if len(starts) > 1:
        raise ValueError('Найдено несколько меток [A]. Сохрани часть A отдельно.')
    start = starts[0] + 1 if starts else 0
    return '\n'.join(lines[start:stop])


def normalise(value):
    return ' '.join(' '.join(clean(line) for line in value.splitlines()).split())


def cosine_tfidf(reference, candidate):
    ref, test = [Counter(re.findall(r'(?u)\b\w\w+\b', text.lower()))
                 for text in (reference, candidate)]
    product = norm_ref = norm_test = 0.0
    for token in sorted(ref.keys() | test.keys()):
        doc_freq = int(token in ref) + int(token in test)
        idf = 1 + math.log(3 / (1 + doc_freq))
        ref_weight, test_weight = ref[token] * idf, test[token] * idf
        product += ref_weight * test_weight
        norm_ref += ref_weight * ref_weight
        norm_test += test_weight * test_weight
    if not norm_ref or not norm_test:
        return 0.0
    return min(1.0, product / math.sqrt(norm_ref * norm_test))


def main():
    try:
        from sacrebleu.metrics import BLEU, CHRF
    except ImportError:
        raise SystemExit('Установи зависимость: python -m pip install sacrebleu==2.6.0')

    bleu = BLEU(lowercase=True, tokenize='13a', smooth_method='exp')
    chrf = CHRF(lowercase=True)
    reference = normalise((ROOT / 'reference_A_en.txt').read_text(encoding='utf-8-sig'))
    rows, problems = [], []
    for model, prompt in RUNS:
        label = f'{model}_{prompt}'
        response = ROOT / 'responses' / f'{label}.txt'
        extracted = ROOT / 'responses' / f'{label}_A.txt'
        try:
            if extracted.exists():
                text = extracted.read_text(encoding='utf-8-sig')
            else:
                text = part_a(response.read_text(encoding='utf-8-sig'))
            candidate = normalise(text)
            if not candidate:
                raise ValueError('Часть A пуста.')
        except (OSError, ValueError) as error:
            problems.append(f'{label}: {error}')
            continue
        rows.append((model, prompt, f'{bleu.corpus_score([candidate], [[reference]]).score:.2f}',
                     f'{cosine_tfidf(reference, candidate):.4f}',
                     f'{chrf.corpus_score([candidate], [[reference]]).score:.2f}'))

    for problem in problems:
        print(problem)
    if not rows:
        raise SystemExit('Добавь ответы в responses/ и запусти расчёт снова.')
    with (ROOT / 'metrics_A.csv').open('w', newline='', encoding='utf-8-sig') as output:
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['model', 'prompt', 'BLEU-4', 'cosine_TFIDF', 'chrF'])
        writer.writerows(rows)
    print(f'metrics_A.csv: {len(rows)} из {len(RUNS)}.')
    if problems:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
