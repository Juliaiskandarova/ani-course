class BowlingGame:
    """Track and score a ten-pin bowling game."""

    def __init__(self) -> None:
        self._frames: list[list[int]] = []
        self._game_over: bool = False

    def roll(self, pins: int) -> None:
        """Record one ball throw.

        Args:
            pins: Number of pins knocked down by this throw.

        Raises:
            TypeError: If pins is not an integer.
            ValueError: If pins is outside the valid range for the current roll.
            RuntimeError: If a roll is attempted in an invalid game state.
        """
        if not isinstance(pins, int) or isinstance(pins, bool):
            raise TypeError("pins must be an integer")
        if pins < 0 or pins > 10:
            raise ValueError("pins must be between 0 and 10")

        if self._game_over:
            raise RuntimeError("cannot roll after the game is over")

        if not self._frames:
            self._frames.append([])
        else:
            last_index = len(self._frames) - 1
            if self._is_frame_complete(last_index, self._frames[last_index]):
                if len(self._frames) == 10:
                    self._game_over = True
                    raise RuntimeError("cannot roll after the game is over")
                self._frames.append([])

        frame_index = len(self._frames) - 1
        frame = self._frames[frame_index]

        if frame_index < 9:
            if len(frame) == 0:
                max_pins = 10
            elif len(frame) == 1:
                if frame[0] == 10:
                    raise RuntimeError("cannot roll twice in a frame after a strike")
                max_pins = 10 - frame[0]
            else:
                raise RuntimeError("cannot roll more than twice in a frame")
        else:
            max_pins = self._max_pins_for_tenth_roll(frame)

        if pins > max_pins:
            raise ValueError(
                f"cannot knock down {pins} pins when only {max_pins} remain"
            )

        frame.append(pins)

        if self._is_frame_complete(frame_index, frame) and frame_index == 9:
            self._game_over = True

    def score(self) -> int:
        """Return the total score for a completed game.

        Raises:
            RuntimeError: If the game is not complete.
        """
        if not self._game_over:
            raise RuntimeError("cannot score before the game is complete")

        all_rolls: list[int] = []
        starts: list[int] = []
        for frame in self._frames:
            starts.append(len(all_rolls))
            all_rolls.extend(frame)

        total = 0
        for frame_index, frame in enumerate(self._frames):
            if frame_index == 9:
                total += sum(frame)
                continue

            if frame[0] == 10:
                total += (
                    10
                    + all_rolls[starts[frame_index] + 1]
                    + all_rolls[starts[frame_index] + 2]
                )
            elif frame[0] + frame[1] == 10:
                total += 10 + all_rolls[starts[frame_index] + 2]
            else:
                total += frame[0] + frame[1]

        return total

    def _is_frame_complete(self, frame_index: int, frame: list[int]) -> bool:
        """Return whether the given frame has no more rolls available."""
        if frame_index < 9:
            return len(frame) == 2 or (len(frame) == 1 and frame[0] == 10)

        if len(frame) == 3:
            return True
        if len(frame) == 2:
            first, second = frame
            return first < 10 and first + second < 10
        return False

    def _max_pins_for_tenth_roll(self, frame: list[int]) -> int:
        """Return the maximum pins allowed for the next tenth-frame roll."""
        if len(frame) == 0:
            return 10
        if len(frame) == 1:
            first = frame[0]
            return 10 if first == 10 else 10 - first
        if len(frame) == 2:
            first, second = frame
            if first == 10:
                return 10 if second == 10 else 10 - second
            if first + second == 10:
                return 10
            raise RuntimeError("cannot roll a third ball in an open tenth frame")
        raise RuntimeError("cannot roll more than three balls in the tenth frame")