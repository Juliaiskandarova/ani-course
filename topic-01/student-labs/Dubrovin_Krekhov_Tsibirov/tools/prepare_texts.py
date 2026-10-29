"""Готовит тексты статей для ЛР1: вырезает авторскую аннотацию и ключевые слова,
убирает колонтитулы/номера страниц/список литературы, склеивает переносы.

Запуск: python prepare_texts.py <ru_fitz.txt> <en_fitz.txt> <out_dir>
(ru_fitz.txt / en_fitz.txt — сырой текст PDF, извлечённый PyMuPDF)
"""
import re
import sys
from pathlib import Path

RU_NOISE = [
    r"^_{10,}\s*$",
    r"^ISSN 2713-",
    r"^ARTIFICIAL INTELLIGENCE, KNOWLEDGE AND DATA ENGINEERING",
    r"^ИСКУССТВЕННЫЙ ИНТЕЛЛЕКТ, ИНЖЕНЕРИЯ ДАННЫХ И ЗНАНИЙ",
    r"^Informatics and Automation\. 2025",
    r"^Информатика и автоматизация\. 2025",
    r"^\d{3}\s*$",  # номера страниц 275–301
]
EN_NOISE = [
    r"^Imane Jaaouine, Ross D\. King\s*$",
    r"^Mitigating Hallucinations in Zero-Shot Scientific Summarisation: A Pilot Study\s*$",
    r"^arXiv:2512\.00931",
    r"^\d{1,2}\s*$",  # номера страниц
]


def drop_noise(lines, patterns):
    rx = [re.compile(p) for p in patterns]
    return [l for l in lines if not any(r.search(l) for r in rx)]


def reflow(lines):
    """Склеивает строки PDF в абзацы: перенос по дефису, слова-по-строке и т.п."""
    text = ""
    prev = ""
    for raw in lines:
        l = raw.strip()
        # короткая строка, закончившаяся точкой, — конец абзаца
        if prev.endswith((".", ":")) and len(prev) < 55 and text and not text.endswith("\n"):
            text += "\n\n"
        prev = l
        if not l:
            text += "\n"
            continue
        if text.endswith("-") and not text.endswith(" -"):
            text = text[:-1] + l  # перенос слова
        elif text and not text.endswith("\n"):
            text += " " + l
        else:
            text += l
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)  # мусор из математических шрифтов
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip() + "\n"


def cut(lines, start_rx, end_rx):
    s = next(i for i, l in enumerate(lines) if re.search(start_rx, l))
    e = next(i for i, l in enumerate(lines) if i > s and re.search(end_rx, l))
    return lines[s:e]


def main(ru_path, en_path, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    ru = Path(ru_path).read_text(encoding="utf8").splitlines()
    ru_abs = cut(ru, r"^Аннотация\. Предложена", r"^Ключевые слова:")
    ru_kw = cut(ru, r"^Ключевые слова:", r"^1\. Введение")
    ru_body = cut(ru, r"^1\. Введение", r"^Литература\s*$")
    title = "Автоматическая генерация аннотаций научных статей на основе больших языковых моделей\n\n"
    (out / "ru_article.txt").write_text(title + reflow(drop_noise(ru_body, RU_NOISE)), encoding="utf8")
    (out / "ru_reference_abstract.txt").write_text(
        reflow(ru_abs).replace("Аннотация. ", "", 1).replace("\n\n", " "), encoding="utf8")
    (out / "ru_keywords.txt").write_text(reflow(ru_kw), encoding="utf8")

    en = Path(en_path).read_text(encoding="utf8").splitlines()
    en_abs = cut(en, r"^Abstract\. Large language", r"^Keywords:")
    en_kw = cut(en, r"^Keywords:", r"^arXiv:2512")
    # тело — от раздела Introduction до списка литературы
    s = next(i for i, l in enumerate(en) if l.strip() == "Introduction") - 1
    e = next(i for i, l in enumerate(en) if l.strip() == "References")
    title = "Mitigating Hallucinations in Zero-Shot Scientific Summarisation: A Pilot Study\n\n"
    (out / "en_article.txt").write_text(title + reflow(drop_noise(en[s:e], EN_NOISE)), encoding="utf8")
    (out / "en_reference_abstract.txt").write_text(
        reflow(en_abs).replace("Abstract. ", "", 1).replace("\n\n", " "), encoding="utf8")
    (out / "en_keywords.txt").write_text(reflow(en_kw), encoding="utf8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
