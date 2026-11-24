class BowlingGame:
    """Score a ten-pin bowling game and reject every rule violation.

    All deliveries are stored in a flat list, and :meth:`score` walks that
    list frame by frame, so strike and spare bonuses may cross frame
    borders. The deliveries of the frame in progress are tracked separately
    because the standing-pin count depends on the frame number. After every
    accepted delivery a self-check verifies the internal invariants of the
    game state.
    """

    FRAME_COUNT = 10
    PIN_COUNT = 10
    MAX_DELIVERIES = 21

    def __init__(self) -> None:
        self._rolls: list[int] = []
        self._frame: list[int] = []
        self._frame_index = 0
        self._finished = False

    def roll(self, pins: int) -> None:
        """Record one delivery of the ball.

        Args:
            pins: Pins knocked down, an integer within 0..10.

        Raises:
            ValueError: On a non-integer or out-of-range value, on a
                delivery that exceeds the standing pins, or on a delivery
                after the game has ended.
        """
        if self._finished:
            raise ValueError("Game over: ten frames have already been played.")
        self._require_int(pins)

        standing = self._standing_pins()
        if pins > standing:
            raise ValueError(
                f"Rule violation: {pins} pins cannot fall while {standing} stand."
            )

        self._rolls.append(pins)
        self._frame.append(pins)
        self._advance()
        self._check_invariants()

    def score(self) -> int:
        """Return the total score of the completed game.

        Raises:
            ValueError: If the game is not finished yet.
        """
        if not self._finished:
            raise ValueError("Game is not over yet: no final score.")

        total = 0
        index = 0
        for _ in range(self.FRAME_COUNT):
            first = self._rolls[index]
            if first == self.PIN_COUNT:
                total += first + self._rolls[index + 1] + self._rolls[index + 2]
                index += 1
            elif first + self._rolls[index + 1] == self.PIN_COUNT:
                total += self.PIN_COUNT + self._rolls[index + 2]
                index += 2
            else:
                total += first + self._rolls[index + 1]
                index += 2
        return total

    @staticmethod
    def _require_int(pins: int) -> None:
        if isinstance(pins, bool) or not isinstance(pins, int):
            raise ValueError(f"pins must be an int, not {type(pins).__name__}")
        if not 0 <= pins <= 10:
            raise ValueError(f"pins must be within 0..10, got {pins}")

    def _standing_pins(self) -> int:
        if not self._frame:
            return self.PIN_COUNT
        if self._frame_index < self.FRAME_COUNT - 1:
            return self.PIN_COUNT - self._frame[0]
        if len(self._frame) == 1:
            first = self._frame[0]
            return self.PIN_COUNT if first == 10 else self.PIN_COUNT - first
        first, second = self._frame
        if first == 10:
            return self.PIN_COUNT if second == 10 else self.PIN_COUNT - second
        return self.PIN_COUNT

    def _advance(self) -> None:
        if self._frame_index < self.FRAME_COUNT - 1:
            if self._frame[0] == 10 or len(self._frame) == 2:
                self._frame_index += 1
                self._frame = []
            return

        if len(self._frame) == 3:
            self._finished = True
        elif (
            len(self._frame) == 2
            and self._frame[0] != 10
            and sum(self._frame) < 10
        ):
            self._finished = True

    def _check_invariants(self) -> None:
        if len(self._rolls) > self.MAX_DELIVERIES:
            raise AssertionError("Internal error: too many deliveries recorded.")
        if self._frame_index > self.FRAME_COUNT - 1:
            raise AssertionError("Internal error: frame index is out of range.")
        if any(not 0 <= pins <= self.PIN_COUNT for pins in self._rolls):
            raise AssertionError("Internal error: bad delivery values.")
