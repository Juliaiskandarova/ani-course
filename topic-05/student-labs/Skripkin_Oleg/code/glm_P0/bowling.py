class BowlingGame:
    def __init__(self):
        self.rolls = []

    def roll(self, pins: int):
        if not isinstance(pins, int) or pins < 0 or pins > 10:
            raise ValueError("Pins knocked down must be an integer between 0 and 10.")

        frame_idx = 0
        frame = 1
        throw_in_frame = 1
        pins_standing = 10
        total_thrown = 0
        tenth_frame_completed = False

        # First, calculate the state of the game before the current throw
        for i, p in enumerate(self.rolls):
            total_thrown += 1
            if frame < 10:
                if throw_in_frame == 1:
                    if p == 10:  # Strike
                        frame += 1
                    else:
                        pins_standing = 10 - p
                        throw_in_frame = 2
                else:  # Throw 2
                    if p == pins_standing:  # Spare
                        pass
                    frame += 1
                    throw_in_frame = 1
                    pins_standing = 10
            else:  # 10th frame
                if throw_in_frame == 1:
                    pins_standing = 10 - p
                    if p == 10:  # Strike
                        pins_standing = 10
                    throw_in_frame = 2
                elif throw_in_frame == 2:
                    prev_p = self.rolls[-1]
                    if prev_p != 10 and p == pins_standing:  # Spare in 10th
                        pins_standing = 10
                        throw_in_frame = 3
                    elif prev_p == 10:  # Second throw after a strike
                        pins_standing = 10 - p
                        if p < 10:
                            throw_in_frame = 3
                        # If p == 10, throw_in_frame remains 2 for the logic below
                    else:
                        # Open frame on 10th, game ends
                        tenth_frame_completed = True
                elif throw_in_frame == 3:
                    tenth_frame_completed = True

        # Now, validate the current throw (pins) based on the game state
        if tenth_frame_completed:
            raise ValueError("Cannot roll after the 10th frame is completed.")

        if frame < 10:
            if throw_in_frame == 2 and pins > pins_standing:
                raise ValueError("Pins knocked down cannot exceed remaining pins in the frame.")
        else:  # 10th frame
            if throw_in_frame == 1:
                pass  # Any 0-10 is valid
            elif throw_in_frame == 2:
                if self.rolls[-1] != 10 and pins > pins_standing:
                    raise ValueError("Second throw in 10th frame cannot exceed remaining pins.")
            elif throw_in_frame == 3:
                if self.rolls[-1] != 10 and pins > pins_standing:
                    raise ValueError("Third throw in 10th frame cannot exceed remaining pins.")
            else:
                raise ValueError("Cannot roll more than 3 times in the 10th frame.")

        self.rolls.append(pins)

    def score(self) -> int:
        if len(self.rolls) == 0:
            raise ValueError("Game has not been started.")

        total_score = 0
        roll_idx = 0
        frame = 1

        for frame in range(1, 11):
            if roll_idx >= len(self.rolls):
                raise ValueError("Game is not finished: insufficient rolls.")

            if frame < 10:
                if self.rolls[roll_idx] == 10:  # Strike
                    if roll_idx + 2 >= len(self.rolls):
                        raise ValueError("Game is not finished: waiting for bonus rolls after a strike.")
                    total_score += 10 + self.rolls[roll_idx + 1] + self.rolls[roll_idx + 2]
                    roll_idx += 1
                else:
                    if roll_idx + 1 >= len(self.rolls):
                        raise ValueError("Game is not finished: insufficient rolls.")
                    first = self.rolls[roll_idx]
                    second = self.rolls[roll_idx + 1]
                    
                    if first + second > 10:
                        raise ValueError("A frame's score cannot exceed 10 pins.")
                    
                    if first + second == 10:  # Spare
                        if roll_idx + 2 >= len(self.rolls):
                            raise ValueError("Game is not finished: waiting for bonus roll after a spare.")
                        total_score += 10 + self.rolls[roll_idx + 2]
                    else:
                        total_score += first + second
                    roll_idx += 2
            else:  # 10th frame
                remaining_rolls = len(self.rolls) - roll_idx
                first = self.rolls[roll_idx] if roll_idx < len(self.rolls) else 0
                second = self.rolls[roll_idx + 1] if roll_idx + 1 < len(self.rolls) else 0

                if first == 10 or first + second == 10:
                    if remaining_rolls < 3:
                        raise ValueError("Game is not finished: 10th frame requires 3 balls.")
                    total_score += self.rolls[roll_idx] + self.rolls[roll_idx + 1] + self.rolls[roll_idx + 2]
                else:
                    if remaining_rolls < 2:
                        raise ValueError("Game is not finished: 10th frame requires 2 balls.")
                    if remaining_rolls > 2:
                        raise ValueError("Game is finished: cannot roll after open 10th frame.")
                    total_score += self.rolls[roll_idx] + self.rolls[roll_idx + 1]

        return total_score
