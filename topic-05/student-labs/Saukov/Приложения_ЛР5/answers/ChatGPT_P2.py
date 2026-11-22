class BowlingGame:
    """Track rolls and calculate the score of a ten-frame bowling game."""

    def __init__(self) -> None:
        """Initialize an empty bowling game."""
        self._frames: list[list[int]] = [[]]

    def roll(self, pins: int) -> None:
        """Record a roll, enforcing bowling rules and frame boundaries."""
        if type(pins) is not int:
            raise TypeError("The number of pins must be an integer.")

        if not 0 <= pins <= 10:
            raise ValueError("The number of pins must be between 0 and 10.")

        frame_index = len(self._frames) - 1
        frame = self._frames[frame_index]

        if frame_index < 9:
            if not frame:
                frame.append(pins)

                if pins == 10:
                    self._frames.append([])
                return

            if frame[0] + pins > 10:
                raise ValueError(
                    "The total number of pins in a frame cannot exceed 10."
                )

            frame.append(pins)
            self._frames.append([])
            return

        # The tenth frame has special rules for fill balls.
        if len(frame) == 3:
            raise ValueError("Cannot roll after the game is complete.")

        if not frame:
            frame.append(pins)
            return

        if len(frame) == 1:
            if frame[0] != 10 and frame[0] + pins > 10:
                raise ValueError(
                    "The total number of pins in a frame cannot exceed 10."
                )

            frame.append(pins)
            return

        # A third roll is permitted only after a strike or spare.
        first, second = frame

        if first != 10 and first + second < 10:
            raise ValueError("Cannot roll after the game is complete.")

        # After a tenth-frame strike, the first fill ball resets
        # the pins only if it is also a strike.
        if first == 10 and second != 10:
            if second + pins > 10:
                raise ValueError(
                    "Fill balls cannot knock down more than 10 pins "
                    "without a new rack."
                )

        frame.append(pins)

    def score(self) -> int:
        """Return the final score of a completed bowling game.

        Raises:
            ValueError: If the game has not been completed.
        """
        if len(self._frames) != 10:
            raise ValueError("Cannot calculate the score of an incomplete game.")

        tenth = self._frames[9]

        if len(tenth) < 2:
            raise ValueError("Cannot calculate the score of an incomplete game.")

        if len(tenth) == 2:
            if tenth[0] == 10 or sum(tenth) == 10:
                raise ValueError(
                    "Cannot calculate the score: "
                    "the tenth frame requires an additional fill ball."
                )

        rolls = [
            pins
            for frame in self._frames
            for pins in frame
        ]

        total = 0
        roll_index = 0

        # Score the first nine frames, including strike and spare bonuses.
        for _ in range(9):
            first = rolls[roll_index]

            if first == 10:
                # Strike: 10 plus the next two throws.
                total += (
                    10
                    + rolls[roll_index + 1]
                    + rolls[roll_index + 2]
                )
                roll_index += 1
                continue

            second = rolls[roll_index + 1]

            if first + second == 10:
                # Spare: 10 plus the next throw.
                total += 10 + rolls[roll_index + 2]
            else:
                # Open frame: only the pins knocked down.
                total += first + second

            roll_index += 2

        # The tenth frame includes its fill balls without extra bonuses.
        total += sum(tenth)

        return total