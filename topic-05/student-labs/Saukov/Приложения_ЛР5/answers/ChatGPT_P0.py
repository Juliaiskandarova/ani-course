
class BowlingGame:
    def __init__(self):
        self._rolls = []
        self._frame = 1
        self._first_roll = None
        self._tenth_rolls = []
        self._finished = False

    def roll(self, pins: int) -> None:
        if type(pins) is not int or not 0 <= pins <= 10:
            raise ValueError("Pins must be an integer from 0 to 10.")

        if self._finished:
            raise ValueError("The game is already complete.")

        if self._frame < 10:
            if self._first_roll is None:
                if pins == 10:
                    self._frame += 1
                else:
                    self._first_roll = pins
            else:
                if self._first_roll + pins > 10:
                    raise ValueError("Too many pins in one frame.")

                self._first_roll = None
                self._frame += 1

        else:
            count = len(self._tenth_rolls)

            if count == 1:
                first = self._tenth_rolls[0]
                if first < 10 and first + pins > 10:
                    raise ValueError("Too many pins in frame 10.")

            elif count == 2:
                first, second = self._tenth_rolls
                if first == 10 and second < 10:
                    if second + pins > 10:
                        raise ValueError("Invalid fill ball.")

            self._tenth_rolls.append(pins)

            if count == 1:
                first, second = self._tenth_rolls
                if first < 10 and first + second < 10:
                    self._finished = True

            elif count == 2:
                self._finished = True

        self._rolls.append(pins)

    def score(self) -> int:
        if not self._finished:
            raise ValueError("The game is not finished yet.")

        total = 0
        i = 0

        for _ in range(9):
            if self._rolls[i] == 10:
                total += (
                    10 + self._rolls[i + 1]
                    + self._rolls[i + 2]
                )
                i += 1

            elif self._rolls[i] + self._rolls[i + 1] == 10:
                total += 10 + self._rolls[i + 2]
                i += 2

            else:
                total += self._rolls[i] + self._rolls[i + 1]
                i += 2

        return total + sum(self._rolls[i:])
