class BowlingGame:
    """Track rolls and calculate the score of a ten-frame bowling game."""

    def __init__(self) -> None:
        """Initialize a new game."""
        self._rolls: list[int] = []
        self._frame = 1
        self._frame_rolls: list[int] = []
        self._complete = False

    def roll(self, pins: int) -> None:
        """Record a legal roll in the current frame."""
        if type(pins) is not int or not 0 <= pins <= 10:
            raise ValueError("pins must be an integer between 0 and 10")
        if self._complete:
            raise ValueError("cannot roll after the game is complete")

        previous = self._frame_rolls

        if self._frame < 10:
            if previous and previous[0] + pins > 10:
                raise ValueError("roll exceeds the pins remaining in this frame")

            self._rolls.append(pins)
            previous.append(pins)

            if pins == 10 or len(previous) == 2:
                self._frame += 1
                self._frame_rolls = []
            return

        if len(previous) == 1 and previous[0] != 10:
            if previous[0] + pins > 10:
                raise ValueError("roll exceeds the pins remaining in the tenth frame")
        elif len(previous) == 2 and previous[0] == 10 and previous[1] != 10:
            if previous[1] + pins > 10:
                raise ValueError("fill ball exceeds the pins remaining in the tenth frame")

        self._rolls.append(pins)
        previous.append(pins)

        if len(previous) == 2 and previous[0] != 10:
            if sum(previous) < 10:
                self._complete = True
        elif len(previous) == 3:
            self._complete = True

    def score(self) -> int:
        """Return the final score, provided the game is complete."""
        if not self._complete:
            raise ValueError("cannot score an incomplete game")

        total = 0
        index = 0

        for frame in range(1, 11):
            first = self._rolls[index]

            if frame == 10:
                total += sum(self._rolls[index:])
            elif first == 10:
                total += 10 + self._rolls[index + 1] + self._rolls[index + 2]
                index += 1
            else:
                second = self._rolls[index + 1]
                total += first + second
                if first + second == 10:
                    total += self._rolls[index + 2]
                index += 2

        return total
