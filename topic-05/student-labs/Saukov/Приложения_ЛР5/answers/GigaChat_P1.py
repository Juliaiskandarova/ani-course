class BowlingGame:
    """
    Класс для подсчета очков в игре в боулинг.

    Игра состоит из 10 фреймов. Каждый фрейм может содержать один или два броска.
    В случае открытого фрейма (менее 10 очков) счет равен количеству сбитых кеглей.
    В случае спэра (все 10 кеглей сбиты вторым броском) к 10 добавляется результат следующего броска.
    В случае страйка (все 10 кеглей сбиты первым броском) к 10 добавляются результаты следующих двух бросков.
    В 10-м фрейме при спэре или страйке игрок получает дополнительные бонусные броски (fill balls).
    """

    def __init__(self):
        """
        Инициализирует игру.
        """
        self._rolls: list[int] = []
        self._current_frame: int = 1
        self._first_throw_in_frame: bool = True
        self._frame_scores: list[int] = [0] * 10

    def roll(self, pins: int) -> None:
        """
        Выполняет бросок мяча игроком.

        Аргументы:
            pins: количество сбитых кеглей (от 0 до 10).

        Исключения:
            ValueError: если pins вне допустимого диапазона [0, 10].
            RuntimeError: если игра уже завершена (было вызвано score()).
            RuntimeError: если количество бросков в текущем фрейме недопустимо.
        """
        if score_called:
            raise RuntimeError("Игра уже завершена, вызов roll() недопустим.")
        if pins < 0 or pins > 10:
            raise ValueError(f"Недопустимое количество кеглей: {pins}. Должно быть от 0 до 10.")

        # Проверка корректности количества бросков в фрейме
        if self._current_frame > 10:
            raise RuntimeError("Превышено количество фреймов (10).")

        if not self._first_throw_in_frame:
            # Второй бросок в фрейме
            prev_roll = self._rolls[-1]
            if prev_roll + pins > 10 and prev_roll != 10:
                raise ValueError(
                    f"Сумма кеглей в фрейме превышает 10: {prev_roll} + {pins}."
                )

        self._rolls.append(pins)

        # Обновление фреймов
        if self._first_throw_in_frame:
            if pins == 10:
                # Страйк
                self._frame_scores[self._current_frame - 1] = 10
                self._current_frame += 1
                self._first_throw_in_frame = True
            else:
                # Первый бросок не страйк
                self._first_throw_in_frame = False
        else:
            # Второй бросок
            total_in_frame = self._rolls[-2] + pins
            if total_in_frame == 10:
                # Спэр
                self._frame_scores[self._current_frame - 1] = 10
            else:
                # Открытый фрейм
                self._frame_scores[self._current_frame - 1] = total_in_frame

            self._current_frame += 1
            self._first_throw_in_frame = True

        # Проверка, не превышено ли количество фреймов
        if self._current_frame > 10:
            # Проверка, нужны ли дополнительные броски для 10-го фрейма
            if len(self._rolls) < 12:
                raise RuntimeError(
                    "Необходимо выполнить дополнительные броски для 10-го фрейма."
                )

    def score(self) -> int:
        """
        Подсчитывает и возвращает общий счет игры.

        Исключения:
            RuntimeError: если игра еще не завершена (недостаточно бросков).
        """
        global score_called
        score_called = True

        if len(self._rolls) < 10:
            raise RuntimeError("Игра еще не завершена: недостаточно бросков.")

        # Проверка корректности заполнения 10-го фрейма
        if self._frame_scores[9] == 10:
            # Страйк или спэр в 10-м фрейме
            if len(self._rolls) < 12:
                raise RuntimeError(
                    "Недостаточно бросков для подсчета 10-го фрейма со страйком или спэром."
                )
        elif len(self._rolls) > 10:
            raise RuntimeError(
                "Дополнительные броски разрешены только при страйке или спэре в 10-м фрейме."
            )

        total_score = 0
        roll_index = 0

        for frame in range(10):
            if self._frame_scores[frame] == 10:
                # Страйк или спэр
                if frame == 9:
                    # 10-й фрейм: просто сумма всех бросков
                    total_score += sum(self._rolls[roll_index:])
                    break

                if self._rolls[roll_index] == 10:
                    # Страйк
                    total_score += 10 + self._rolls[roll_index + 1] + self._rolls[roll_index + 2]
                    roll_index += 1
                else:
                    # Спэр
                    total_score += 10 + self._rolls[roll_index + 2]
                    roll_index += 2
            else:
                # Открытый фрейм
                total_score += self._frame_scores[frame]
                roll_index += 2

        return total_score


# Вспомогательная переменная для отслеживания вызова score()
score_called = False