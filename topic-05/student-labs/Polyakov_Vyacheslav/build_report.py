"""Build the PDF report from preserved experiment results."""
from pathlib import Path
import json
import os
import textwrap
from html import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted, Flowable

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'Отчёт_ЛР5_Поляков.pdf'
FONT = Path(os.environ.get('REPORT_FONT_DIR', '/tmp/polyakov-times-fonts'))
for name, filename in [('Body', 'Times.TTF'), ('Bold', 'Timesbd.TTF'),
                       ('Sans', 'Times.TTF'), ('Italic', 'Timesi.TTF')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT / filename)))
pdfmetrics.registerFont(TTFont('Mono', '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf'))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Italic', boldItalic='Bold')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('Text', fontName='Body', fontSize=14, leading=21,
                         firstLineIndent=12.5*mm, alignment=TA_JUSTIFY,
                         spaceAfter=0, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle('SmallText', fontName='Body', fontSize=12, leading=18,
                         alignment=TA_JUSTIFY, spaceAfter=6, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle('TableText', fontName='Body', fontSize=12, leading=14.4,
                         alignment=TA_LEFT))
styles.add(ParagraphStyle('TableHeader', parent=styles['TableText'], fontName='Bold'))
styles.add(ParagraphStyle('PromptText', fontName='Body', fontSize=12, leading=14.4,
                         alignment=TA_LEFT, spaceAfter=2, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle('Head', fontName='Bold', fontSize=14, leading=21,
                         alignment=TA_CENTER, spaceAfter=18, keepWithNext=True))
styles.add(ParagraphStyle('Sub', fontName='Bold', fontSize=14, leading=21,
                         firstLineIndent=12.5*mm, spaceBefore=12, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle('Caption', fontName='Body', fontSize=12, leading=18,
                         spaceBefore=12, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle('CodeSmall', fontName='Mono', fontSize=10, leading=12, spaceBefore=6, spaceAfter=6))
story = []
W = A4[0] - 45*mm - 12
table_number = 0
page_call = 0
results = json.loads((ROOT / 'analysis/results.json').read_text())
env = json.loads((ROOT / 'analysis/environment.json').read_text())
names = {'deepseek': 'DeepSeek', 'alice': 'Алиса AI', 'qwen': 'Qwen3.7-Plus'}


def para(text, style='Text'):
    return Paragraph(escape(text).replace('\n', '<br/>'), styles[style])


def p(text, style='Text'):
    story.append(para(text, style))


def heading(text):
    p(text.upper(), 'Head')


def page():
    global page_call
    page_call += 1
    # Keep the main discussion continuous, avoiding nearly empty continuation pages.
    if 2 <= page_call <= 6:
        story.append(Spacer(1, 21))
    else:
        story.append(PageBreak())


def table(rows, widths, small=True):
    global table_number
    table_number += 1
    titles = ['Правила задачи Bowling', 'Модели и условия генерации',
              'Среда проверки', 'Итоговые метрики', 'Причины провалов',
              'Дополнительные проверки', 'Результаты статического анализа']
    p(f'Таблица {table_number} — {titles[table_number-1]}', 'Caption')
    cells = [[para(str(value), 'TableHeader' if index == 0 else 'TableText')
              for value in row] for index, row in enumerate(rows)]
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 9))


def code(text):
    lines = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, int(W/6), replace_whitespace=False, drop_whitespace=False) or [''])
    story.append(Preformatted('\n'.join(lines), styles['CodeSmall']))


class CoverBlock(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = W, 700

    def draw(self):
        c = self.canv
        c.setFont('Body', 14)
        for y, text in [(686, 'Министерство науки и высшего образования Российской Федерации'),
                        (665, 'Санкт-Петербургский политехнический университет Петра Великого')]:
            c.drawCentredString(W/2, y, text)
        c.setFont('Bold', 16)
        c.drawCentredString(W/2, 480, 'ОТЧЁТ')
        c.setFont('Body', 14)
        for y, text in [(456, 'по лабораторной работе № 5'), (432, '«Генерация кода по описанию»'),
                        (408, 'Задача Bowling'), (384, 'по дисциплине «Автоматизация научных исследований»')]:
            c.drawCentredString(W/2, y, text)
        c.drawRightString(W, 205, 'Выполнил студент группы 5040102/60201')
        c.drawRightString(W, 184, 'Поляков Вячеслав')
        c.drawCentredString(W/2, 18, 'Санкт-Петербург')
        c.drawCentredString(W/2, -3, '2026')


story.append(CoverBlock())
page()

heading('1 Цель и постановка эксперимента')
p('Цель работы — сравнить код трёх языковых моделей при последовательном добавлении инструкций к промпту. Проверяются функциональная корректность, цикломатическая сложность и замечания статического анализатора. В данном эксперименте лучший результат DeepSeek получен с P1; у Алисы P1 ухудшил результат, а P2 восстановил его. Qwen прошёл исходные тесты во всех версиях, однако дополнительные проверки обнаружили ограничения P0 и P2.')
p('Выбрана задача Bowling из материалов темы 5. Программа реализует класс BowlingGame, методы roll(pins: int) и score() -> int. Полное английское условие включено в каждый сохранённый промпт. Имя класса уточнено одинаково во всех трёх промптах, поскольку его ожидает готовый набор тестов.')
table([
    ['Правило', 'Содержание'],
    ['Открытый фрейм', 'Менее 10 кеглей за два броска; очки равны их сумме.'],
    ['Спэр', '10 кеглей за два броска; бонус равен следующему броску.'],
    ['Страйк', '10 кеглей первым броском; бонус равен следующим двум броскам.'],
    ['Десятый фрейм', 'После спэра один дополнительный бросок, после страйка два. Они не дают новых бросков.'],
    ['Ограничения', 'Нельзя сбить больше стоящих кеглей, бросать после завершения и считать незавершённую игру. Нарушения сообщаются через raise с понятным сообщением.'],
], [105, W - 105])
p('P0 содержит базовую просьбу решить задачу. P1 добавляет роль разработчика, Python 3.11, стандартную библиотеку, фиксированный интерфейс, обработку ошибок, docstring и аннотации типов. P2 дополнительно требует составить список правил и проверить по нему черновик до вывода. Внутренняя самопроверка модели непосредственно не наблюдается; оценивается только выданный код.')
p('Собраны девять предоставленных ответов: три модели × три промпта. Исходная логика решений не исправлялась. Один и тот же файл из 31 теста применён ко всем программам; затем выполнен статический анализ и отдельно — исследовательские проверки пробелов в тестовом покрытии.')
page()

heading('2 Протокол и условия проверки')
table([
    ['Модель', 'Отображаемый режим', 'Материалы'],
    ['DeepSeek', 'На скриншотах Search выделен, DeepThink не выделен. Версия модели не показана.', 'P0, P1, P2; код, ответы и скриншоты'],
    ['Алиса AI', 'Интеллект: Авто; над ответами указан режим «Эксперт». Версия не показана.', 'P0, P1, P2; код, ответы и скриншоты'],
    ['Qwen3.7-Plus', 'Auto; Thinking completed.', 'P0, P1, P2; код, ответы и скриншоты'],
], [90, 245, W - 335])
p('Дата получения материалов — 23.11.2026. Ответы сопоставлены с моделями по совпадению начала кода со скриншотами. Скриншоты фиксируют состояние интерфейса после ответа, поэтому не доказывают настройки на момент запуска. Запуски были запрошены в отдельных новых чатах; непрерывная запись действий не велась.')
p('У Qwen P2 виден индикатор «2/2». Предыдущая альтернатива не предоставлена; причина появления индикатора неизвестна. Поэтому корректная единица наблюдения здесь — один полученный ответ на пару модель–промпт, а не гарантированно первая и единственная генерация. pass@k не рассчитывается.')
p('Полные текстовые вложения сохранены для Алисы P0 и DeepSeek P1/P2. Остальные ответы переданы кодом в сообщениях; при сохранении декодированы экранирование Markdown и HTML-обозначения пробелов. Логика, комментарии и имена сохранены; пробелы, пустые строки и завершающий перевод строки могут отличаться от оригинального представления. Это ограничивает точную воспроизводимость замечаний о форматировании.')
table([
    ['Компонент', 'Фактическое значение'],
    ['Python', env['python'] + '; Linux. В промптах целевая версия 3.11.'],
    ['pytest / Radon / Pylint', ' / '.join(env['tools'][name] for name in ('pytest', 'radon', 'pylint'))],
    ['Тесты', '31 тест из локального снимка Exercism; tests/bowling_test.py скопирован без изменений.'],
    ['Pylint', 'Стандартные правила, --rcfile=/dev/null, --persistent=n, --py-version=3.11. Все файлы анализировались как bowling.py.'],
], [105, W - 105])
p('Все девять файлов успешно разобраны ast.parse с feature_version=(3, 11). Это проверка синтаксиса Python 3.11; выполнение в CPython 3.11 не проводилось. Фактические динамические результаты относятся к Python 3.12.14.', 'SmallText')
page()

heading('3 Методика и итоговые метрики')
p('TPR = N_passed / 31 × 100%. Любое падение или ошибка теста считается непройденной проверкой. CC max — максимальная сложность функции или метода из radon cc; агрегированная оценка класса исключена. Pylint Score — фактический балл анализатора с нижней границей 0; исходный балл также сохранён. Округление в таблице выполнено только при отображении.')
rows = [['Модель', 'Промпт', 'Пройдено', 'TPR, %', 'CC max', 'Pylint']]
for r in results:
    rows.append([names[r['model']], r['prompt'], f"{r['passed']}/{r['total']}",
                 f"{r['tpr']:.2f}", r['cc_max'], f"{r['pylint_score']:.2f}"])
table(rows, [107, 55, 70, 75, 65, W - 372])
for model in names:
    subset = [r for r in results if r['model'] == model]
    delta = subset[-1]['tpr'] - subset[0]['tpr']
    p(f"{names[model]}: P0 → P2, изменение TPR {delta:+.2f} п.п.; CC max {subset[0]['cc_max']} → {subset[-1]['cc_max']}; Pylint {subset[0]['pylint_score']:.2f} → {subset[-1]['pylint_score']:.2f}.")
p('Все 31 тест прошли шесть из девяти программ. Всего успешно выполнены 247 из 279 проверок; 32 проверки завершились неуспешно. Средние значения TPR по моделям: P0 — 69,89%, P1 — 97,85%, P2 — 97,85%. Одинаковое среднее P1/P2 скрывает изменения конкретных моделей.')
p('Статические метрики не заменяют тесты. DeepSeek P0 имеет Pylint 9,44 при TPR 9,68%. DeepSeek P2 получает 9,90 и минимальный CC max 8, но ошибается в двух тестах. У Qwen P2 оценка Pylint выше, чем у P1, хотя CC max вырос с 15 до 19, а дополнительные проверки выявляют регрессию поведения.')
page()

heading('4 Проваленные тесты и причины')
table([
    ['Версия', 'Провалы', 'Причина и наблюдаемое поведение'],
    ['DeepSeek P0', '28 из 31', '_is_game_over вызывает _last_frame_start до накопления бросков. _last_frame_start без проверки длины обходит девять фреймов. Уже первый допустимый roll вызывает IndexError. Большинство сценариев не достигает проверки своего основного условия.'],
    ['Алиса P1', '2 из 31', 'После страйка в десятом фрейме кегли безусловно выставляются заново перед третьим броском, даже если второй бросок сбил менее 10. Принимаются 10, 5, 6 и 10, 6, 10.'],
    ['DeepSeek P2', '2 из 31', '_validate_tenth_frame_roll при first == 10 сразу выполняет return. Ограничение третьего броска числом 10 - second отсутствует. Принимаются те же два недопустимых варианта.'],
], [90, 65, W - 155])
p('Два одинаковых теста, проваленных Алисой P1 и DeepSeek P2:', 'Sub')
code('test_two_bonus_rolls_after_a_strike_in_the_last_frame_cannot_score_more_than_10_points\ntest_the_second_bonus_rolls_after_a_strike_in_the_last_frame_cannot_be_a_strike_if_the_first_one_is_not_a_strike')
p('В обоих случаях сначала разыгрываются девять нулевых фреймов. В десятом фрейме после 10 и 5 остаётся пять кеглей, поэтому 6 должно вызвать исключение. После 10 и 6 остаётся четыре, поэтому следующий страйк невозможен. Тесты завершились AssertionError: Exception not raised.')
p('Три формально успешных теста DeepSeek P0 проверяют отрицательное значение, значение выше 10 и score() до начала игры. Первые два отклоняются явной валидацией. Третий проходит из-за случайного IndexError: тест требует любое исключение с непустым сообщением и не различает предметную ошибку и аварийный доступ к списку. Поэтому даже эти 3/31 не означают три корректно реализованных сценария.')
p('В коде DeepSeek P0 также виден return в ветке дополнительных бросков до self.rolls.append(pins). Этот дефект отмечен по исходному тексту; основной прогон не изолирует его, поскольку раньше возникает IndexError. Отдельное исправление кода для проверки этой гипотезы не выполнялось.')
p('Полный поимённый перечень всех 32 неуспешных проверок с сообщениями и трассировками находится в analysis/failures.csv; JUnit XML и текст pytest сохранены отдельно для каждой версии.')
page()

heading('5 Дополнительный качественный разбор')
p('После основного прогона выполнены одинаковые исследовательские проверки для всех девяти решений. Они не включены в исходный набор из 31 теста и не изменяют TPR. Сценарии и результаты воспроизводятся supplementary.py и сохранены в analysis/supplementary.json.')
table([
    ['Проверка', 'Результат'],
    ['roll(True) и roll(1.5) в новой игре', 'Qwen P0/P2 принимают оба значения. Qwen P1 и все версии Алисы/DeepSeek отклоняют их. Проверки целочисленного интерфейса отсутствуют в исходных 31 тестах.'],
    ['Продолжение после отклонённого броска', 'roll(5), попытка roll(6), затем roll(5) и 18 нулей: ожидается итог 10. Семь версий дают 10. DeepSeek P0 аварийно завершается раньше; Qwen P2 после отклонения 6 уже повредил состояние и отвергает следующий допустимый 5.'],
    ['score() в пустой игре', 'DeepSeek P0 возвращает случайный IndexError: list index out of range. Другие версии явно сообщают о незавершённости игры.'],
], [155, W - 155])
p('Почему Qwen P2 портит состояние', 'Sub')
code('self.rolls.append(pins)\n...\nself.pins_remaining -= pins\nif self.pins_remaining < 0:\n    raise ValueError("Pin count exceeds pins on the lane")')
p('После первого броска 5 остаётся пять кеглей. Ошибочный бросок 6 уже записан в список и уменьшает остаток до -1, после чего выбрасывается исключение. Повторный допустимый бросок 5 работает с испорченным состоянием. Исходные тесты проверяют факт исключения, но не продолжение игры после него. Самопроверка в P2 не предотвратила этот дефект.')
p('В Qwen P1 проверка pins > self.pins_remaining предшествует изменению данных; в исследовательском сценарии состояние сохраняется и игра корректно завершается с 10 очками. Поэтому при одинаковом основном TPR 100% версия P1 предпочтительнее P2 по рассмотренным свойствам.')
p('Приём bool и дробного числа оценивается как ограничение соответствия интерфейсу pins: int. Для требования о сохранении состояния после ошибки применяется инженерная интерпретация: отклонённый бросок не должен учитываться. Эти дополнительные критерии не объявляются частью исходного тестового контракта.')
page()

heading('6 Выводы и воспроизводимость')
p('Усложнение промпта не гарантировало последовательного улучшения. Для DeepSeek инструкции P1 устранили аварийную ошибку P0 и повысили TPR с 9,68% до 100%, но P2 снизил результат до 93,55%. Для Алисы P1 внёс ошибку бонусных бросков, а P2 восстановил 100%. Qwen сохранил 100% на исходном наборе, однако P2 ухудшил валидацию типов и сохранность состояния после ошибки по сравнению с P1.')
p('В рамках полученных материалов наиболее убедительны DeepSeek P1, Алиса P2 и Qwen P1: они прошли основной набор и рассмотренные дополнительные сценарии. Это локальный вывод по одной задаче и одному полученному ответу на комбинацию. Он не является рейтингом моделей в целом. Более высокий Pylint и меньший CC не доказывают корректность, а 100% TPR характеризует только выбранное покрытие.')
p('Ограничения: одна задача; малое число наблюдений; неизвестные версии DeepSeek и Алисы; неполная фиксация режима при генерации; индикатор 2/2 у Qwen P2; широкие проверки типа исключения в тестах; фактический запуск на Python 3.12 вместо целевого 3.11; возможные отличия пробелов при переносе ответов. Дополнительные проверки выбраны после просмотра кода и приведены как исследовательские, без изменения исходного набора.')
p('Повторение расчёта', 'Sub')
p('Из каталога работы создайте отдельное окружение Python, установите версии из requirements.txt и выполните команды:', 'Text')
code('python -m pip install -r requirements.txt\npython analyze.py\npython supplementary.py')
p('analyze.py копирует каждое решение и неизменный тестовый файл во временный каталог, запускает pytest, Radon и Pylint. Скрипт сохраняет исходные журналы, JSON результатов, CSV метрик и провалов, версии среды, контрольные суммы кода. Воспроизведение с другой версией Python или зависимостей может изменить результаты статического анализа.')
p('SHA-256 тестового файла', 'Sub')
code(textwrap.fill(env['test_sha256'], 40))
p('Источники и состав приложений', 'Sub')
p('Материалы темы 5: «Генерация кода по описанию.pptx», слайды 22–23; «Промты.docx». Тестовый файл — локальная неизменённая копия из приложений ЛР5 Saukov; в его заголовке указан Exercism и дата 2023-07-21. Адрес исходного проекта: https://github.com/exercism/python/tree/main/exercises/practice/bowling.', 'SmallText')
p('prompts/ — полные запросы; answers/ — девять ответов, извлечённый код и скриншоты; tests/ — набор и сведения об источнике; analysis/ — метрики, провалы, журналы и среда; protocol.csv — протокол получения. Далее приведены полные промпты и примеры скриншотов. Остальные скриншоты и весь код приложены отдельными файлами.', 'SmallText')
page()

for prompt in ('P0', 'P1', 'P2'):
    heading(f'Приложение А Полный промпт {prompt}')
    for block in (ROOT / 'prompts' / f'{prompt}.txt').read_text().split('\n\n'):
        p(block, 'PromptText')
    page()

heading('Приложение Б Статический анализ')
rows = [['Модель', 'Промпт', 'Метод с CC max', 'CC', 'E', 'W', 'R', 'C']]
for r in results:
    rows.append([names[r['model']], r['prompt'], r['cc_method'], r['cc_max'],
                 r['error'], r['warning'], r['refactor'], r['convention']])
table(rows, [90, 55, 145, 35, 30, 30, 30, W - 415])
p('E — ошибки, W — предупреждения, R — предложения рефакторинга, C — замечания по соглашениям. Fatal-замечаний нет. CC вычислен по методу, а не по агрегированной оценке класса. Полные сообщения с номерами строк находятся в *_pylint.json; все блоки сложности — в *_radon.json.')
p('В Pylint стандартная формула учитывает категории с разными весами и число операторов; численные баллы в отчёте взяты непосредственно из JSON анализатора. Даже отсутствие E у DeepSeek P0 не выявляет аварийный доступ к списку на первом броске.')
page()

for model in ('deepseek', 'alice', 'qwen'):
    heading('Приложение В Скриншот ' + names[model] + ' P2')
    p('Начало сохранённого ответа и отображаемые настройки. Все девять исходных скриншотов находятся рядом с соответствующими ответами.', 'SmallText')
    img = Image(str(ROOT / 'answers' / model / 'P2/screenshot.png'))
    ratio = min(W / img.imageWidth, 610 / img.imageHeight)
    img.drawWidth = img.imageWidth * ratio
    img.drawHeight = img.imageHeight * ratio
    story.append(img)
    if model != 'qwen':
        page()


def footer(canvas, doc):
    if doc.page > 1:
        canvas.setFont('Body', 12)
        canvas.drawCentredString(A4[0] / 2, 10*mm, str(doc.page))


SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=15*mm, leftMargin=30*mm,
                  topMargin=20*mm, bottomMargin=20*mm, title='ЛР5 Генерация кода по описанию Поляков Вячеслав',
                  author='Поляков Вячеслав').build(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
