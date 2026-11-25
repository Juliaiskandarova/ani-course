# Лабораторная работа № 5

Скрипкин Олег

Сравнение GLM 5.2, GPT-6 Sol и DeepSeek V4.1 Flash на задаче подсчёта очков в боулинге. Для каждой модели выполнены три независимых запроса.

- [Отчёт PDF](report.pdf) и [отчёт Word](report.docx).
- [Постановка](task.txt), [промпты P0–P2](prompts) и [исходные ответы API](responses).
- [Девять реализаций](code), [метрики](analysis/metrics.csv) и [разбор 34 упавших проверок](analysis/failure_causes.csv).
- [Набор тестов Exercism из работы В. Полякова](tests/bowling_test.py) и [лицензия](tests/LICENSE).

Из 279 проверок пройдено 245. DeepSeek V4.1 Flash с P1 прошла 31 из 31, получила CC max 8 и Pylint 9,86. Все три ответа GPT-6 Sol прошли 31 из 31.

Для воспроизведения из папки работы выполните две команды.

    python -m pip install -r requirements.txt
    python analyze.py
