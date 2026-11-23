class BowlingGame:
    """Учёт очков в боулинге (10 фреймов)."""

    MAX_PINS = 10
    TOTAL_FRAMES = 10

    def __init__(self):
        self._rolls = []

    def roll(self, pins: int):
        # Валидация отдельного броска
        if not isinstance(pins, int) or isinstance(pins, bool):
            raise ValueError("Number of pins must be an integer")
        if pins < 0:
            raise ValueError("Number of pins cannot be negative")
        if pins > self.MAX_PINS:
            raise ValueError("Number of pins cannot exceed 10")

        standing = self._pins_standing_now()
        if standing is None:
            raise IndexError("Game is already over, cannot roll more balls")
        if pins > standing:
            raise ValueError(
                f"Cannot knock down {pins} pins, only {standing} are standing"
            )

        self._rolls.append(pins)

    def score(self) -> int:
        # score() вызывается только по завершении игры
        if self._pins_standing_now() is not None:
            raise IndexError("Game is not finished yet, cannot score")

        return self._compute_score()

    # ---------- внутренние методы ----------

    def _pins_standing_now(self):
        """Сколько кеглей стоит перед следующим броском; None — игра окончена."""
        rolls = self._rolls
        i = 0

        # Первые 9 фреймов: один или два броска
        for _ in range(self.TOTAL_FRAMES - 1):
            if i >= len(rolls):                       # фрейм только начался
                return self.MAX_PINS
            if rolls[i] == self.MAX_PINS:             # strike — фрейм завершён
                i += 1
            elif i + 1 < len(rolls):                  # есть второй бросок
                i += 2
            else:                                     # ждём второй бросок
                return self.MAX_PINS - rolls[i]

        # 10-й фрейм
        if i >= len(rolls):
            return self.MAX_PINS
        frame_rolls = rolls[i:]
        first = frame_rolls[0]

        if first == self.MAX_PINS:                    # strike — до трёх бросков
            rest = frame_rolls[1:]
            if len(rest) >= 2:
                return None                           # три броска сыграны — конец
            if len(rest) == 1:
                return self.MAX_PINS if rest[0] == self.MAX_PINS else self.MAX_PINS - rest[0]
            return self.MAX_PINS

        if len(frame_rolls) == 1:                     # ждём второй бросок
            return self.MAX_PINS - first

        second = frame_rolls[1]
        if first + second == self.MAX_PINS:           # spare — нужен fill-бросок
            return None if len(frame_rolls) >= 3 else self.MAX_PINS
        return None                                   # open frame — конец игры

    def _compute_score(self) -> int:
        rolls = self._rolls
        total = 0
        i = 0

        for _ in range(self.TOTAL_FRAMES):
            if rolls[i] == self.MAX_PINS:                   # strike
                total += self.MAX_PINS + rolls[i + 1] + rolls[i + 2]
                i += 1
            elif rolls[i] + rolls[i + 1] == self.MAX_PINS:  # spare
                total += self.MAX_PINS + rolls[i + 2]
                i += 2
            else:                                           # open frame
                total += rolls[i] + rolls[i + 1]
                i += 2

        return total
