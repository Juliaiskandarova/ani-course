class BowlingGame:
    """Keep track of the score of a ten-pin bowling game."""

    def __init__(self) -> None:
        self._rolls: list[int] = []
        self._frame: int = 1
        self._ball: int = 1
        self._pins_standing: int = 10
        self._tenth_rolls: int = 0
        self._tenth_first_roll: int | None = None
        self._game_over: bool = False

    def roll(self, pins: int) -> None:
        """Record a ball throw.

        Args:
            pins: Number of pins knocked down by this throw.

        Raises:
            TypeError: If pins is not an integer.
            ValueError: If pins is negative, greater than 10, or greater than
                the number of standing pins.
            RuntimeError: If a roll is attempted after the game is complete.
        """
        if isinstance(pins, bool) or not isinstance(pins, int):
            raise TypeError("pins must be an integer")
        if self._game_over:
            raise RuntimeError("cannot roll after the game is complete")
        if pins < 0:
            raise ValueError("pins cannot be negative")
        if pins > 10:
            raise ValueError("pins cannot exceed 10")
        if pins > self._pins_standing:
            raise ValueError(
                f"pins ({pins}) cannot exceed the number of standing pins "
                f"({self._pins_standing})"
            )

        self._rolls.append(pins)

        if self._frame < 10:
            if self._ball == 1:
                if pins == 10:
                    self._advance_frame()
                else:
                    self._pins_standing -= pins
                    self._ball = 2
            else:
                self._advance_frame()
            return

        self._tenth_rolls += 1
        self._pins_standing -= pins

        if self._tenth_rolls == 1:
            self._tenth_first_roll = pins
            if pins == 10:
                self._pins_standing = 10
            self._ball = 2
        elif self._tenth_rolls == 2:
            first = self._tenth_first_roll
            if first == 10:
                if pins == 10:
                    self._pins_standing = 10
                self._ball = 3
            elif first is not None and first + pins == 10:
                self._pins_standing = 10
                self._ball = 3
            else:
                self._game_over = True
        else:
            self._game_over = True

    def score(self) -> int:
        """Return the total score for the completed game.

        Raises:
            RuntimeError: If the game is not complete yet.
        """
        if not self._game_over:
            raise RuntimeError("cannot score before the game is complete")

        total = 0
        index = 0

        for _ in range(10):
            if self._rolls[index] == 10:
                total += 10 + self._rolls[index + 1] + self._rolls[index + 2]
                index += 1
            elif self._rolls[index] + self._rolls[index + 1] == 10:
                total += 10 + self._rolls[index + 2]
                index += 2
            else:
                total += self._rolls[index] + self._rolls[index + 1]
                index += 2

        return total

    def _advance_frame(self) -> None:
        """Move to the next frame and reset frame-local state."""
        self._frame += 1
        self._ball = 1
        self._pins_standing = 10