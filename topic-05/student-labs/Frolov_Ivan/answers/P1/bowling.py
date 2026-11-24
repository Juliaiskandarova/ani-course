class BowlingGame:
    """Score a single ten-pin bowling game.

    The object is stateful: every call to :meth:`roll` records one delivery,
    and :meth:`score` becomes available only after the tenth frame and all
    fill balls have been played.
    """

    FRAMES = 10
    PINS = 10

    def __init__(self) -> None:
        """Start a new game with ten empty frames."""
        self._frames: list[list[int]] = [[]]
        self._finished: bool = False

    def roll(self, pins: int) -> None:
        """Record one delivery.

        Args:
            pins: Pins knocked down by the delivery, an integer from 0 to 10.

        Raises:
            ValueError: If the game is already complete, the value is not a
                valid number of pins, or the delivery exceeds the number of
                pins still standing.
        """
        if self._finished:
            raise ValueError("Cannot roll: the tenth frame is already complete.")
        self._validate_pins(pins)

        frame = self._frames[-1]
        standing = self._standing_pins(frame)
        if pins > standing:
            raise ValueError(
                f"Cannot knock down {pins} pins: only {standing} are standing."
            )

        frame.append(pins)
        self._advance(frame)

    def score(self) -> int:
        """Return the total score of the complete game.

        Raises:
            ValueError: If the game is not complete yet.
        """
        if not self._finished:
            raise ValueError("Cannot score: the game is not complete.")

        rolls = [pins for frame in self._frames for pins in frame]
        total = 0
        index = 0

        for frame in self._frames[:-1]:
            total += sum(frame)
            total += self._bonus(frame, rolls, index)
            index += len(frame)

        return total + sum(self._frames[-1])

    @staticmethod
    def _validate_pins(pins: int) -> None:
        if isinstance(pins, bool) or not isinstance(pins, int):
            raise ValueError(f"Pins must be int, got {type(pins).__name__}.")
        if not 0 <= pins <= 10:
            raise ValueError(f"Pins must be between 0 and 10, got {pins}.")

    @staticmethod
    def _bonus(frame: list[int], rolls: list[int], index: int) -> int:
        if frame[0] == 10:
            return rolls[index + 1] + rolls[index + 2]
        if sum(frame) == 10:
            return rolls[index + 2]
        return 0

    def _standing_pins(self, frame: list[int]) -> int:
        if not frame:
            return self.PINS
        if len(self._frames) < self.FRAMES:
            return self.PINS - frame[0]
        if len(frame) == 1:
            return self.PINS if frame[0] == 10 else self.PINS - frame[0]
        first, second = frame
        if first == 10:
            return self.PINS if second == 10 else self.PINS - second
        return self.PINS

    def _advance(self, frame: list[int]) -> None:
        if len(self._frames) < self.FRAMES:
            if frame[0] == 10 or len(frame) == 2:
                self._frames.append([])
            return

        if len(frame) == 3:
            self._finished = True
        elif len(frame) == 2 and frame[0] != 10 and sum(frame) != 10:
            self._finished = True
