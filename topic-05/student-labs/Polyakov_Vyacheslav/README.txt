Лабораторная работа №5 — Поляков Вячеслав

Основной файл: Отчёт_ЛР5_Поляков.pdf (16 страниц).
prompts/ — P0, P1, P2 с одинаковым условием Bowling.
answers/<модель>/<промпт>/ — response.txt, bowling.py, screenshot.png, SOURCE.txt.
tests/ — неизменный набор 31 теста и сведения об источнике.
analysis/results.json и metrics.csv — итоговые результаты pytest/Radon/Pylint.
analysis/failures.csv — все 32 провала из 279 проверок.
analysis/*_pytest.xml и *_pytest.txt — журналы функциональных тестов.
analysis/*_radon.json и *_pylint.json — статический анализ.
analysis/supplementary.json — дополнительные исследовательские проверки, не входящие в TPR.
protocol.csv — сопоставление моделей, промптов и скриншотов.

Воспроизведение в отдельной среде Python 3.12:
python -m pip install -r requirements.txt
python analyze.py
python supplementary.py

Фактический прогон: Python 3.12.14. Синтаксис проверен для Python 3.11; исполнение на 3.11 не проводилось.
Сборка PDF: build_report.py, пакет reportlab, Times New Roman и Liberation Mono для кода.
REPORT_FONT_DIR задаёт каталог с файлами Times.TTF, Timesbd.TTF, Timesi.TTF.
Оформление: Times New Roman 14 пт, интервал 1,5, абзац 1,25 см; поля слева 3 см, справа 1,5 см, сверху и снизу 2 см.
Таблицы и технические приложения — 12 пт. Шрифты встроены в PDF; для просмотра устанавливать их не нужно.
Исходный код моделей не исправлен. Особенности переноса из сообщений описаны в SOURCE.txt и отчёте.
