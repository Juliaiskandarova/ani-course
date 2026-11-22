class BowlingGame:
    """
    Класс для подсчёта очков в игре боулинг.

    Поддерживает два метода:
        - roll(pins: int) — фиксация результата броска.
        - score(): int — получение итогового счёта (только после завершения игры).

    Правила:
        - 10 фреймов.
        - В фрейме 1–2 броска.
        - Страйк: 10 + следующие два броска.
        - Спэр: 10 + следующий бросок.
        - 10-й фрейм: при страйке/спэре — дополнительные броски.
    """

    def __init__(self) -> None:
        self._frames: list[list[int]] = [[] for _ in range(10)]
        self._current_frame: int = 0
        self._roll_in_frame: int = 0
        self._score_calculated: bool = False

    def _check_game_active(self) -> None:
        if self._score_calculated:
            raise RuntimeError("Игра уже завершена, нельзя делать броски.")
        if self._current_frame >= 10:
            raise RuntimeError("Превышено количество фреймов.")

    def _check_pins(self, pins: int) -> None:
        if not isinstance(pins, int) or pins < 0 or pins > 10:
            raise ValueError("Число кеглей должно быть целым от 0 до 10.")

    def _check_roll_valid(self, pins: int) -> None:
        self._check_game_active()
        self._check_pins(pins)

        frame = self._frames[self._current_frame]
        if self._roll_in_frame == 0:
            # Первый бросок в фрейме
            if pins == 10 and self._current_frame != 9:
                # Страйк — сразу закрываем фрейм
                pass
            else:
                frame.append(pins)
                self._roll_in_frame = 1
        else:
            # Второй бросок
            if frame[0] + pins > 10:
                raise ValueError(
                    f"Сумма кеглей за фрейм не может превышать 10 (было {frame[0]} + {pins})."
                )
            frame.append(pins)
            # Закрываем фрейм
            self._current_frame += 1
            self._roll_in_frame = 0

    def roll(self, pins: int) -> None:
        """
        Фиксирует результат броска.

        :param pins: Число сбитых кеглей (0–10).
        :raises ValueError: Если pins вне диапазона.
        :raises RuntimeError: Если игра завершена или фрейм переполнен.
        """
        self._check_roll_valid(pins)

        frame = self._frames[self._current_frame]
        if self._roll_in_frame == 0 and not (
            pins == 10 and self._current_frame != 9
        ):
            frame.append(pins)
            self._roll_in_frame = 1
        elif self._roll_in_frame == 0 and pins == 10 and self._current_frame != 9:
            # Страйк — фрейм закрывается сразу
            frame.append(pins)
            self._current_frame += 1
        elif self._roll_in_frame == 1:
            frame.append(pins)
            self._current_frame += 1
            self._roll_in_frame = 0

    def score(self) -> int:
        """
        Возвращает итоговый счёт игры.

        :return: Сумма очков за все фреймы.
        :raises RuntimeError: Если игра ещё не завершена.
        """
        if self._score_calculated:
            raise RuntimeError("Итоговый счёт уже был получен.")

        # Проверка, что игра завершена
        if self._current_frame < 10:
            raise RuntimeError("Игра ещё не завершена — не хватает фреймов.")
        if self._current_frame == 10 and len(self._frames[9]) < 3 and (
            self._frames[9][0] != 10 and len(self._frames[9]) < 2
        ):
            raise RuntimeError("Не завершён 10-й фрейм.")

        total = 0
        for i in range(10):
            frame = self._frames[i]
            if i < 9:
                # Обычные фреймы
                if frame[0] == 10:
                    # Страйк
                    total += 10
                    # Бонусы
                    if i + 1 < 10:
                        if self._frames[i + 1][0] == 10:
                            # Два страйка подряд
                            if i + 2 < 10:
                                total += self._frames[i + 2][0]
                            else:
                                raise RuntimeError(
                                    "Не хватает данных для подсчёта страйка."
                                )
                        else:
                            total += self._frames[i + 1][0]
                            if len(self._frames[i + 1]) > 1:
                                total += self._frames[i + 1][1]
                            else:
                                raise RuntimeError(
                                    "Не хватает данных для подсчёта страйка."
                                )
                elif sum(frame) == 10:
                    # Спэр
                    total += 10
                    total += self._frames[i + 1][0]
                else:
                    # Открытый фрейм
                    total += sum(frame)
            else:
                # 10-й фрейм — просто сумма
                total += sum(frame)

        self._score_calculated = True
        return total