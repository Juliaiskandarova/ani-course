class BowlingGame:
    """Represents a game of bowling."""

    def __init__(self) -> None:
        """Initialize a new bowling game."""
        self.rolls: list[int] = []
        self.current_frame: int = 1
        self.current_roll_in_frame: int = 1
        self.pins_remaining: int = 10
        self.fill_balls_remaining: int = 0
        self.game_over: bool = False

    def roll(self, pins: int) -> None:
        """Record a roll of `pins` knocked down."""
        if pins < 0 or pins > 10:
            raise ValueError("Pins must have value from 0 to 10")
        if self.game_over:
            raise ValueError("Cannot roll after game is over")
        
        self.rolls.append(pins)
        
        if self.current_frame == 10:
            if self.current_roll_in_frame == 1:
                self.pins_remaining -= pins
                if self.pins_remaining < 0:
                    raise ValueError("Pin count exceeds pins on the lane")
                if pins == 10:
                    self.fill_balls_remaining = 2
                    self.pins_remaining = 10
                else:
                    self.fill_balls_remaining = 0
                self.current_roll_in_frame += 1
            elif self.current_roll_in_frame == 2:
                if self.fill_balls_remaining == 2:
                    self.pins_remaining -= pins
                    if self.pins_remaining < 0:
                        raise ValueError("Pin count exceeds pins on the lane")
                    if pins == 10:
                        self.fill_balls_remaining = 1
                        self.pins_remaining = 10
                    else:
                        self.fill_balls_remaining = 1
                    self.current_roll_in_frame += 1
                else:
                    self.pins_remaining -= pins
                    if self.pins_remaining < 0:
                        raise ValueError("Pin count exceeds pins on the lane")
                    if self.pins_remaining == 0:
                        self.fill_balls_remaining = 1
                        self.pins_remaining = 10
                        self.current_roll_in_frame += 1
                    else:
                        self.game_over = True
            elif self.current_roll_in_frame == 3:
                self.pins_remaining -= pins
                if self.pins_remaining < 0:
                    raise ValueError("Pin count exceeds pins on the lane")
                self.game_over = True
        else:
            self.pins_remaining -= pins
            if self.pins_remaining < 0:
                raise ValueError("Pin count exceeds pins on the lane")
            if self.pins_remaining == 0 or self.current_roll_in_frame == 2:
                self.current_frame += 1
                self.current_roll_in_frame = 1
                self.pins_remaining = 10
            else:
                self.current_roll_in_frame += 1

    def score(self) -> int:
        """Return the total score of the game."""
        if not self.game_over:
            raise ValueError("Cannot get score before game is over")
        
        total_score = 0
        roll_index = 0
        
        for frame in range(1, 11):
            if frame < 10:
                if self.rolls[roll_index] == 10:
                    total_score += 10 + self.rolls[roll_index + 1] + self.rolls[roll_index + 2]
                    roll_index += 1
                else:
                    frame_score = self.rolls[roll_index] + self.rolls[roll_index + 1]
                    if frame_score == 10:
                        total_score += 10 + self.rolls[roll_index + 2]
                    else:
                        total_score += frame_score
                    roll_index += 2
            else:
                total_score += sum(self.rolls[roll_index:])
                
        return total_score
