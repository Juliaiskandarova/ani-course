# bowling.py
from typing import List


class BowlingGame:
    def __init__(self) -> None:
        self._rolls: List[int] = []
        self._frame = 1
        self._throws_in_frame = 0
        self._frame_pins = 0
        self._tenth_rolls: List[int] = []
        self._game_over = False

    def roll(self, pins: int) -> None:
        if isinstance(pins, bool) or not isinstance(pins, int):
            raise ValueError("Pins must be an integer")

        if not 0 <= pins <= 10:
            raise ValueError("Pins must be between 0 and 10")

        if self._game_over:
            raise ValueError("Cannot roll: the game is already over")

        if self._frame <= 9:
            if self._throws_in_frame == 0:
                self._rolls.append(pins)

                if pins == 10:
                    self._frame += 1
                    self._throws_in_frame = 0
                    self._frame_pins = 0
                else:
                    self._throws_in_frame = 1
                    self._frame_pins = pins
            else:
                if pins > 10 - self._frame_pins:
                    raise ValueError(
                        f"Invalid roll: {pins} pins would exceed the pins "
                        f"standing in frame {self._frame}"
                    )

                self._rolls.append(pins)
                self._frame += 1
                self._throws_in_frame = 0
                self._frame_pins = 0
            return

        # Tenth frame
        if len(self._tenth_rolls) == 0:
            self._tenth_rolls.append(pins)
            self._rolls.append(pins)

        elif len(self._tenth_rolls) == 1:
            first = self._tenth_rolls[0]

            if first == 10:
                # Fresh rack for the first fill ball.
                self._tenth_rolls.append(pins)
                self._rolls.append(pins)
            else:
                if pins > 10 - first:
                    raise ValueError(
                        f"Invalid roll: {pins} pins would exceed the pins "
                        "standing in the tenth frame"
                    )

                self._tenth_rolls.append(pins)
                self._rolls.append(pins)

                if first + pins < 10:
                    self._game_over = True

        elif len(self._tenth_rolls) == 2:
            first, second = self._tenth_rolls

            if first == 10:
                max_pins = 10 if second == 10 else 10 - second
            else:
                # first + second == 10, otherwise the game would already be over.
                max_pins = 10

            if pins > max_pins:
                raise ValueError(
                    f"Invalid roll: {pins} pins would exceed the pins "
                    "standing in the tenth frame"
                )

            self._tenth_rolls.append(pins)
            self._rolls.append(pins)
            self._game_over = True

        else:
            raise ValueError("Cannot roll: the game is already over")

    def score(self) -> int:
        if not self._game_over:
            raise ValueError(
                "Score can only be calculated after the game is complete"
            )

        total = 0
        i = 0

        for _ in range(10):
            if self._rolls[i] == 10:
                total += 10 + self._rolls[i + 1] + self._rolls[i + 2]
                i += 1
            elif self._rolls[i] + self._rolls[i + 1] == 10:
                total += 10 + self._rolls[i + 2]
                i += 2
            else:
                total += self._rolls[i] + self._rolls[i + 1]
                i += 2

        return total