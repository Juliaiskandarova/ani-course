class BowlingGame:
    """Track rolls and calculate the score of a ten-frame bowling game."""

    def __init__(self) -> None:
        """Initialize a new bowling game."""
        self._frames: list[list[int]] = [[] for _ in range(10)]
        self._frame_index: int = 0

    def roll(self, pins: int) -> None:
        """Record a roll, validating pin counts and bowling rules.

        Args:
            pins: Number of pins knocked down, from 0 to 10.

        Raises:
            TypeError: If pins is not an integer.
            ValueError: If pins is outside the valid range or the
                roll knocks down more pins than are standing.
            RuntimeError: If the game is already complete.
        """
        if self._frame_index >= 10:
            raise RuntimeError("Cannot roll: the bowling game is complete.")

        if isinstance(pins, bool) or not isinstance(pins, int):
            raise TypeError("Pins must be an integer between 0 and 10.")

        if not 0 <= pins <= 10:
            raise ValueError("Pins must be between 0 and 10.")

        frame = self._frames[self._frame_index]

        if self._frame_index < 9:
            if frame and frame[0] + pins > 10:
                raise ValueError(
                    f"Frame {self._frame_index + 1}: "
                    "the total number of knocked-down pins "
                    "cannot exceed 10."
                )

            frame.append(pins)

            if pins == 10 or len(frame) == 2:
                self._frame_index += 1

            return

        # The tenth frame has special rules for bonus rolls.
        if len(frame) == 1:
            if frame[0] != 10 and frame[0] + pins > 10:
                raise ValueError(
                    "Frame 10: the first two rolls cannot knock down "
                    "more than 10 pins unless the first roll is a strike."
                )

        elif len(frame) == 2:
            if frame[0] == 10:
                if frame[1] != 10 and frame[1] + pins > 10:
                    raise ValueError(
                        "Frame 10: after a strike, the second and third "
                        "rolls cannot knock down more than 10 pins "
                        "unless the second roll is also a strike."
                    )
            elif frame[0] + frame[1] != 10:
                raise RuntimeError(
                    "Frame 10: a bonus roll is allowed only after "
                    "a strike or spare."
                )

        frame.append(pins)

        if len(frame) == 3:
            self._frame_index = 10
        elif len(frame) == 2:
            if frame[0] != 10 and sum(frame) < 10:
                self._frame_index = 10

    def score(self) -> int:
        """Calculate and return the final bowling score.

        Returns:
            The total score of the completed game.

        Raises:
            RuntimeError: If the game is not yet complete.
        """
        if self._frame_index < 10:
            raise RuntimeError(
                "Cannot calculate score: the bowling game "
                "is not yet complete."
            )

        rolls = [
            pins
            for frame in self._frames
            for pins in frame
        ]

        total = 0
        roll_index = 0

        for _ in range(9):
            first = rolls[roll_index]

            if first == 10:
                # Strike: 10 plus the next two rolls.
                total += (
                    10
                    + rolls[roll_index + 1]
                    + rolls[roll_index + 2]
                )
                roll_index += 1
            else:
                second = rolls[roll_index + 1]

                if first + second == 10:
                    # Spare: 10 plus the next roll.
                    total += 10 + rolls[roll_index + 2]
                else:
                    # Open frame: sum of both rolls.
                    total += first + second

                roll_index += 2

        # All rolls in the tenth frame count directly.
        total += sum(self._frames[9])

        return total