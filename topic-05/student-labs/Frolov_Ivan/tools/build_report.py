"""Build report.pdf from the preserved results of the Bowling experiment."""
from pathlib import Path
import json
import os
import textwrap
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Flowable, Image, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
OUTPUT = ROOT / 'report.pdf'
FONT = Path(os.environ.get('REPORT_FONT_DIR', '/tmp/lab5-times-fonts'))
MONO = Path(os.environ.get('REPORT_MONO_FONT', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))

for name, filename in [('Body', 'Times.TTF'), ('Bold', 'Timesbd.TTF'),
                       ('Italic', 'Timesi.TTF')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT / filename)))
pdfmetrics.registerFont(TTFont('Mono', str(MONO)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold',
                              italic='Italic', boldItalic='Bold')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle('BodyText14', fontName='Body', fontSize=14, leading=21,
                          firstLineIndent=12.5 * mm, alignment=TA_JUSTIFY,
                          spaceAfter=0, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle('Small', fontName='Body', fontSize=12, leading=18,
                          alignment=TA_JUSTIFY, spaceAfter=6, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle('H1', fontName='Bold', fontSize=14, leading=21,
                          alignment=TA_CENTER, spaceBefore=6, spaceAfter=12,
                          keepWithNext=True))
styles.add(ParagraphStyle('H2', fontName='Bold', fontSize=14, leading=21,
                          firstLineIndent=12.5 * mm, spaceBefore=10, spaceAfter=6,
                          keepWithNext=True))
styles.add(ParagraphStyle('Caption', fontName='Body', fontSize=12, leading=18,
                          alignment=TA_LEFT, spaceBefore=10, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle('TableText', fontName='Body', fontSize=12, leading=14.4,
                          alignment=TA_LEFT))
styles.add(ParagraphStyle('TableHeader', parent=styles['TableText'], fontName='Bold'))
styles.add(ParagraphStyle('Prompt', fontName='Body', fontSize=11, leading=14,
                          alignment=TA_LEFT, spaceAfter=4))
styles.add(ParagraphStyle('CodeStyle', fontName='Mono', fontSize=8.8, leading=10.6,
                          spaceBefore=4, spaceAfter=8))
styles.add(ParagraphStyle('Source', fontName='Body', fontSize=12, leading=17,
                          alignment=TA_LEFT, spaceAfter=6, leftIndent=18,
                          firstLineIndent=-18))
styles.add(ParagraphStyle('TOC1', fontName='Body', fontSize=14, leading=21, leftIndent=0))
styles.add(ParagraphStyle('TOC2', fontName='Body', fontSize=14, leading=21, leftIndent=18))

env = json.loads((ROOT / 'analysis/environment.json').read_text())
results = json.loads((ROOT / 'analysis/results.json').read_text())
extra = json.loads((ROOT / 'analysis/supplementary.json').read_text())
by_prompt = {row['prompt']: row for row in results}

W = A4[0] - 30 * mm - 15 * mm - 12
story = []
table_count = 0


def para(text, style='BodyText14'):
    return Paragraph(escape(text).replace('\n', '<br/>'), styles[style])


def p(text, style='BodyText14'):
    story.append(para(text, style))


class Heading(Paragraph):
    """Paragraph that is also a table-of-contents entry."""

    def __init__(self, text, level):
        super().__init__(escape(text.upper() if level == 1 else text),
                         styles['H1' if level == 1 else 'H2'])
        self.toc_title = text
        self.toc_level = level - 1


def heading(text, level=1):
    story.append(Heading(text, level))


def code(text):
    rows = []
    for line in text.splitlines():
        rows.extend(textwrap.wrap(line, 82, replace_whitespace=False,
                                  drop_whitespace=False) or [''])
    story.append(Preformatted('\n'.join(rows), styles['CodeStyle']))


def table(rows, widths, title):
    global table_count
    table_count += 1
    p(f'Таблица {table_count} — {title}', 'Caption')
    cells = [[Paragraph(escape(str(value)), styles['TableHeader' if row_index == 0 else 'TableText'])
              for value in row] for row_index, row in enumerate(rows)]
    grid = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    grid.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(grid)
    story.append(Spacer(1, 9))


class Cover(Flowable):
    """Title page drawn without the body-text margins."""

    def __init__(self):
        super().__init__()
        self.width, self.height = W, 712

    def draw(self):
        canvas = self.canv
        canvas.setFont('Body', 13)
        for y, text in [(700, 'Министерство науки и высшего образования Российской Федерации'),
                        (680, 'Санкт-Петербургский политехнический университет Петра Великого')]:
            canvas.drawCentredString(W / 2, y, text)
        canvas.setFont('Bold', 16)
        canvas.drawCentredString(W / 2, 500, 'ОТЧЁТ')
        canvas.setFont('Body', 14)
        for y, text in [(474, 'по лабораторной работе № 5'),
                        (450, '«Генерация программного кода по описанию с помощью LLM»'),
                        (426, 'Задача Bowling'),
                        (392, 'по дисциплине «Автоматизация научных исследований»')]:
            canvas.drawCentredString(W / 2, y, text)
        canvas.drawRightString(W, 215, 'Выполнил студент группы 5040102/60201')
        canvas.drawRightString(W, 194, 'Фролов Иван')
        canvas.drawCentredString(W / 2, 30, 'Санкт-Петербург')
        canvas.drawCentredString(W / 2, 8, '2026')


class Report(SimpleDocTemplate):
    """DocTemplate that feeds the table of contents."""

    def afterFlowable(self, flowable):
        if isinstance(flowable, Heading):
            self.notify('TOCEntry', (flowable.toc_level, flowable.toc_title, self.page - 1))


story.append(Cover())
story.append(PageBreak())

story.append(Paragraph('СОДЕРЖАНИЕ', styles['H1']))
toc = TableOfContents()
toc.levelStyles = [styles['TOC1'], styles['TOC2']]
toc.dotsMinLevel = 0
story.append(toc)
story.append(PageBreak())

heading('1 Цель работы и формат эксперимента')
p('Цель работы — проверить, как последовательное уточнение промпта влияет на '
  'корректность и качество кода, который языковая модель генерирует по текстовому '
  'описанию задачи. В качестве задачи выбрана Bowling из материалов темы 5: '
  'подсчёт очков в десятифреймовой партии в боулинг. Сравниваются три версии '
  'запроса с одинаковым условием, но с разным объёмом требований к коду.')
p('Каждое решение проверяется одним и тем же набором из 31 теста, а затем '
  'оценивается статически: максимальная цикломатическая сложность (CC max) по '
  'Radon и балл Pylint. Дополнительно проводятся несколько проверок, которых нет '
  'в исходном наборе тестов; они не входят в основной процент и приведены отдельно.')
p('Все три ответа получены от одной модели (DeepSeek) в отдельных чатах, поэтому '
  'различия между решениями связаны только с текстом промпта, а не со сменой модели.')

heading('2 Постановка задачи Bowling')
p('Партия состоит из десяти фреймов. В каждом фрейме игроку доступны две попытки '
  'при полном наборе из десяти кеглей, если первый бросок не сбил все кегли. '
  'Правила подсчёта очков приведены в таблице 1 и соответствуют слайду методических '
  'материалов (materials/image.png).')
table([
    ['Правило', 'Условие', 'Очки'],
    ['Открытый фрейм', 'Меньше 10 кеглей за два броска', 'Число сбитых кеглей'],
    ['Спэр', 'Все 10 кеглей вторым броском', '10 + кегли следующего броска'],
    ['Страйк', 'Все 10 кеглей первым броском', '10 + кегли двух следующих бросков'],
    ['Десятый фрейм', 'Спэр даёт 1 дополнительный бросок, страйк — 2',
     'Дополнительные броски не дают новых; очки равны сумме сбитых кеглей'],
], [95, 175, W - 270], 'Правила подсчёта очков в задаче Bowling')
p('Требуемый интерфейс — класс BowlingGame с методами roll(pins: int) и '
  'score() -> int. Метод score вызывается только в конце партии. Любое нарушение '
  'правил игры или подсчёта должно приводить к исключению с осмысленным сообщением; '
  'именно это требование отделяет корректную реализацию от реализации, которая '
  'молча принимает невозможные броски.')
p('Полное английское условие дословно включено в каждый из трёх промптов, поэтому '
  'различия в решениях не связаны с разным пониманием задачи.')

heading('3 Промпты P0, P1 и P2')
p('P0 содержит только просьбу написать решение задачи на Python и полный текст '
  'условия. Никаких требований к стилю, типам, обработке ошибок и формату ответа '
  'в нём нет.')
p('P1 добавляет роль senior-разработчика, целевую версию Python 3.11, запрет '
  'сторонних библиотек, требование не менять интерфейс, явно обработать все '
  'некорректные сценарии через raise, добавить docstring и аннотации типов, а также '
  'выдать ответ одним блоком кода без пояснений.')
p('P2 сохраняет все требования P1 и добавляет два обязательных шага: сначала '
  'составить полный список правил предметной области, затем проверить по этому '
  'списку собственный черновик и исправить расхождения до вывода ответа. '
  'Внутренняя самопроверка модели напрямую не наблюдаема, поэтому по P2 оценивается '
  'только итоговый код.')
p('Полные тексты промптов находятся в каталоге prompts/ (файлы P0.txt, P1.txt, '
  'P2.txt) и приведены в приложении А.')

heading('4 Протокол и воспроизводимость')
table([
    ['Параметр', 'Значение'],
    ['Модель', 'DeepSeek; номер версии в интерфейсе не отображался'],
    ['Дата получения ответов', '24.11.2026'],
    ['Организация эксперимента', 'Три отдельных чата, по одному на промпт; повторные генерации не запрашивались'],
    ['Сохранение ответов', 'answers/P0/response.txt и аналогичные файлы для P1 и P2 — ответ целиком'],
    ['Извлечение кода', 'answers/P0/bowling.py и аналогичные файлы для P1 и P2 — блок кода из ответа без правок логики'],
    ['Тесты', 'tests/bowling_test.py, 31 тест Exercism, файл не изменялся'],
], [150, W - 150], 'Условия получения и сохранения ответов')
p('Код извлекался из ответа механически: отбрасывались пояснения вокруг блока '
  'кода, сам код не редактировался. Это важно, потому что иначе метрики описывали '
  'бы не ответ модели, а последующую ручную правку.')
p('Ограничение протокола: скриншоты интерфейса и настройки генерации в комплект '
  'не включены, поэтому единица наблюдения — один сохранённый ответ на промпт, '
  'а не гарантированно первая генерация. При таком объёме данных результаты '
  'описывают конкретные три ответа, а не модель в целом; pass@k не рассчитывается.')

heading('5 Методика оценки')
p('Функциональная корректность измеряется долей пройденных тестов: '
  'TPR = N(пройдено) / N(всего) × 100 %. Набор содержит 31 тест и покрывает '
  'расчёт очков, бонусы за спэр и страйк, специальные правила десятого фрейма, '
  'запрет лишних бросков, выход за диапазон 0..10, невозможность сбить больше '
  'стоящих кеглей, а также запрет считать незавершённую партию. Сто процентов TPR '
  'означают успех на этом наборе, но не доказательство отсутствия всех дефектов.')
p('Статический анализ выполняется на копии файла с именем bowling.py, потому что '
  'именно этот модуль импортируют тесты. CC max — максимальная сложность функции '
  'или метода по Radon; агрегированная оценка класса исключена, так как она '
  'складывается из методов. Балл Pylint получен со стандартными правилами '
  '(--rcfile=/dev/null, --persistent=n, --py-version=3.11) и ограничен снизу нулём.')
table([
    ['Компонент', 'Фактическое значение'],
    ['Python', env['python'] + '; Linux. Целевая версия в промптах — 3.11.'],
    ['pytest / Radon / Pylint', ' / '.join(env['tools'][name] for name in ('pytest', 'radon', 'pylint'))],
    ['Тесты', f"{env['test_count']} тестов Exercism; SHA-256 {env['test_sha256']}"],
    ['Проверка синтаксиса', 'ast.parse с feature_version=(3, 11) для всех трёх файлов'],
], [135, W - 135], 'Среда проверки')
p('Синтаксис всех трёх решений разобран как Python 3.11, однако фактическое '
  'исполнение проводилось на Python 3.12.3: интерпретатор 3.11 в среде отсутствовал. '
  'Для использованных конструкций это не влияет на поведение, но формально '
  'результаты получены на другой версии, чем указана в промптах.', 'Small')

heading('6 Результаты эксперимента')
rows = [['Промпт', 'Пройдено', 'TPR, %', 'CC max', 'Метод с CC max', 'Pylint']]
for prompt in ('P0', 'P1', 'P2'):
    row = by_prompt[prompt]
    rows.append([prompt, f"{row['passed']}/{row['total']}", f"{row['tpr']:.2f}",
                 row['cc_max'], row['cc_method'], f"{row['pylint_score']:.2f}"])
table(rows, [55, 70, 60, 55, 145, W - 385], 'Измеренные показатели трёх запусков')
p('Все три решения прошли 31 тест из 31: и базовая просьба, и два уточнённых '
  'промпта дали функционально корректную программу на этом наборе. Различия '
  'проявились в статических метриках: максимальная сложность метода упала с 17 '
  'у P0 до 8 у P1 и P2, а балл Pylint вырос с 9,09 до 9,83 и 9,86 соответственно.')
p('В P0 наиболее сложным оказался метод roll: он совмещает проверку значения, '
  'вычисление числа стоящих кеглей для обычного и десятого фрейма, запись броска '
  'и определение момента завершения партии. В P1 и P2 эта логика разложена на '
  'вспомогательные методы, поэтому максимальная сложность одного метода снизилась '
  'более чем вдвое.')

heading('7 Анализ решений и дополнительных проверок')
heading('P0: минимальная реализация', 2)
p('Ответ на базовый промпт содержит класс без docstring и аннотаций типов, с '
  'сообщениями об ошибках на русском языке. Значение проверяется только на '
  'попадание в диапазон 0..10: отдельной проверки типа нет, поэтому True и 1.5 '
  'принимаются как допустимые броски, а строка приводит к TypeError вместо '
  'ValueError с осмысленным сообщением. Тесты этого не обнаруживают, так как '
  'требуют лишь любое исключение для явно недопустимых чисел.')
code('if not 0 <= pins <= 10:\n'
     '    raise ValueError(f"Бросок должен сбивать от 0 до 10 кеглей, получено {pins}.")')
heading('P1: декомпозиция и строгий интерфейс', 2)
p('P1 вводит проверку типа с явным исключением bool, выносит валидацию, начисление '
  'бонуса, подсчёт стоящих кеглей и переход к следующему фрейму в отдельные методы, '
  'добавляет docstring и аннотации. Сообщения об ошибках сформулированы на '
  'английском языке и указывают конкретную причину отказа.')
code('@staticmethod\n'
     'def _validate_pins(pins: int) -> None:\n'
     '    if isinstance(pins, bool) or not isinstance(pins, int):\n'
     '        raise ValueError(f"Pins must be int, got {type(pins).__name__}.")')
heading('P2: самопроверка и журнал бросков', 2)
p('P2 меняет представление данных: все броски хранятся в одном плоском списке, а '
  'score проходит по нему пофреймово, поэтому бонусы естественно пересекают границы '
  'фреймов. Дополнительно после каждого принятого броска выполняется проверка '
  'внутренних инвариантов: число бросков не превышает 21, индекс фрейма остаётся в '
  'допустимых пределах, журнал не содержит значений вне диапазона.')
code('def _check_invariants(self) -> None:\n'
     '    if len(self._rolls) > self.MAX_DELIVERIES:\n'
     '        raise AssertionError("Internal error: too many deliveries recorded.")')
heading('Дополнительные проверки', 2)
p('Официальные тесты проверяют только факт исключения. Дополнительно проверялось, '
  'принимает ли реализация значения нецелого типа и сохраняет ли состояние игры '
  'после отклонённого броска. Результаты сведены в таблицу 5 и сохранены в '
  'analysis/supplementary.json.')
rows = [['Проверка', 'P0', 'P1', 'P2']]
names = {'roll_true': 'roll(True)', 'roll_float': 'roll(1.5)', 'roll_str': 'roll("3")'}
for key in ('roll_true', 'roll_float', 'roll_str'):
    cells = [names[key]]
    for prompt in ('P0', 'P1', 'P2'):
        item = extra[prompt][key]
        cells.append('принято' if item['accepted'] else f"отклонено ({item['exception']})")
    rows.append(cells)
resume = ['Продолжение после отклонённого броска']
for prompt in ('P0', 'P1', 'P2'):
    item = extra[prompt]['resume_after_rejection']
    resume.append(f"счёт {item['score']}" if item['score'] is not None else 'ошибка')
rows.append(resume)
table(rows, [150, 85, 85, W - 320], 'Дополнительные проверки вне набора из 31 теста')
p('Расхождение обнаружено только у P0: он принимает True и 1.5, то есть нарушает '
  'заявленный интерфейс roll(pins: int). P1 и P2 отклоняют все три значения через '
  'ValueError. Состояние после отклонённого броска не портит ни одно решение: во '
  'всех трёх случаях партия корректно завершается со счётом 10.')

heading('8 Сопоставление трёх запросов')
p('Функциональная корректность. Усложнение промпта не изменило TPR: P0, P1 и P2 '
  'дают 100 %. Это ожидаемо, поскольку полный текст правил и требование '
  'использовать raise уже присутствуют в базовом промпте, а набор тестов не '
  'проверяет типы аргументов.')
p('Цикломатическая сложность. Переход P0 → P1 снизил CC max с 17 до 8: требования '
  'к структуре кода и docstring подтолкнули модель к разбиению метода roll на '
  'небольшие функции. Переход P1 → P2 не изменил CC max, хотя добавил отдельный '
  'метод самопроверки: он простой и на максимум не влияет.')
p('Pylint. Балл вырос с 9,09 у P0 до 9,83 у P1 (+0,74) и почти не изменился у P2 '
  '(9,86, +0,03). Прирост P0 → P1 объясняется docstring, аннотациями и более '
  'короткими методами; P2 добавляет проверки, но сохраняет тот же уровень '
  'оформления. Разница 0,03 находится в пределах влияния одного-двух замечаний '
  'анализатора и не должна интерпретироваться как содержательное превосходство.')
p('Интерпретация. На этой задаче базовый промпт оказался достаточным для '
  'функциональной корректности, но уступил в строгости интерфейса и читаемости. '
  'Промпт P1 дал основной измеримый выигрыш. Промпт P2, требующий явной '
  'самопроверки, не изменил ни TPR, ни CC, ни балл Pylint заметным образом; его '
  'вклад виден только в появлении метода проверки инвариантов, то есть в '
  'дополнительной защите, а не в измеренных показателях.')

heading('9 Заключение')
p('В работе получены три решения задачи Bowling от одной модели при разном уровне '
  'детализации промпта. Все три прошли полный набор из 31 теста. Уточнение промпта '
  'улучшило статические показатели: максимальная цикломатическая сложность '
  'снизилась с 17 до 8, балл Pylint вырос с 9,09 до 9,83–9,86. Дополнительная '
  'инструкция о самопроверке в P2 не дала измеримого прироста относительно P1.')
p('Дополнительные проверки показали, что базовый промпт не обеспечивает строгого '
  'соответствия интерфейсу pins: int, тогда как явное требование обработать '
  'некорректные сценарии в P1 и P2 это исправляет. Основной набор тестов такой '
  'дефект не выявляет, поэтому статические метрики и дополнительные проверки '
  'дополняют, но не заменяют тестирование.')
p('Ограничения: одна задача, один сохранённый ответ на промпт, отсутствие '
  'скриншотов и фиксации настроек генерации, исполнение на Python 3.12 вместо '
  'целевой версии 3.11. Выводы относятся к полученным ответам и не являются '
  'рейтингом модели.')

story.append(PageBreak())
heading('Приложение А. Полные тексты промптов')
for prompt, subtitle in [('P0', 'A.1 P0 — базовый промпт'),
                         ('P1', 'A.2 P1 — ограничения и интерфейс'),
                         ('P2', 'A.3 P2 — обязательная самопроверка')]:
    heading(subtitle, 2)
    for block in (ROOT / 'prompts' / f'{prompt}.txt').read_text(encoding='utf-8').split('\n\n'):
        p(block.strip(), 'Prompt')
    story.append(PageBreak())

heading('Приложение Б. Исходный код решений')
for prompt, subtitle in [('P0', 'Б.1 P0 — решение по базовому промпту'),
                         ('P1', 'Б.2 P1 — решение с ограничениями'),
                         ('P2', 'Б.3 P2 — решение с самопроверкой')]:
    heading(subtitle, 2)
    code((ROOT / 'answers' / prompt / 'bowling.py').read_text(encoding='utf-8').rstrip())
    story.append(PageBreak())

heading('Приложение В. Источники')
p('1. Методические материалы темы 5: «Генерация кода по описанию.pptx», '
  '«Промты.docx», «Отчёт_доклад_генерация_кода.docx».', 'Source')
p('2. Слайд «Задача Bowling: правила подсчёта» — файл materials/image.png.',
  'Source')
p('3. Exercism Python track, упражнение bowling: '
  'https://github.com/exercism/python/tree/main/exercises/practice/bowling. '
  'Тестовый файл bowling_test.py получен из локальных приложений ЛР5 и не '
  'изменялся; контрольная сумма указана в tests/SOURCE.txt.', 'Source')
p('4. Radon 6.0.1 и Pylint 4.1.4 — документация инструментов статического '
  'анализа.', 'Source')


def footer(canvas, doc):
    if doc.page > 1:
        canvas.setFont('Body', 12)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, str(doc.page - 1))


document = Report(str(OUTPUT), pagesize=A4, leftMargin=30 * mm, rightMargin=15 * mm,
                  topMargin=20 * mm, bottomMargin=20 * mm,
                  title='ЛР5 Генерация кода по описанию — Фролов Иван',
                  author='Фролов Иван')
document.multiBuild(story, onFirstPage=footer, onLaterPages=footer)
print(OUTPUT)
