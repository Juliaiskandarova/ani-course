"""ROUGE-1 и ROUGE-L (F1) для русских и английских текстов.

Предобработка как советуют на слайде 15: нижний регистр, без пунктуации,
ё → е, без стемминга и без стоп-слов. Готовые библиотеки (rouge-score)
выбрасывают кириллицу при токенизации, поэтому своя реализация.

Запуск: python rouge.py <эталон.txt> <кандидат.txt> [...]
"""
import re
import sys
from collections import Counter
from pathlib import Path


def tokens(text):
    text = text.lower().replace("ё", "е")
    return re.findall(r"[0-9a-zа-я]+(?:[-'][0-9a-zа-я]+)*", text)


def f1(match, n_ref, n_cand):
    if not match:
        return 0.0
    r, p = match / n_ref, match / n_cand
    return 2 * p * r / (p + r)


def rouge1(ref, cand):
    overlap = sum((Counter(ref) & Counter(cand)).values())
    return f1(overlap, len(ref), len(cand))


def lcs_len(a, b):
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def rougeL(ref, cand):
    return f1(lcs_len(ref, cand), len(ref), len(cand))


def score(ref_text, cand_text):
    ref, cand = tokens(ref_text), tokens(cand_text)
    return {"rouge1": rouge1(ref, cand), "rougeL": rougeL(ref, cand),
            "words": len(cand_text.split())}


if __name__ == "__main__":
    ref = Path(sys.argv[1]).read_text(encoding="utf8")
    for p in sys.argv[2:]:
        s = score(ref, Path(p).read_text(encoding="utf8"))
        print(f"{p}: ROUGE-1 {s['rouge1']*100:.1f}%  ROUGE-L {s['rougeL']*100:.1f}%  {s['words']} слов")
