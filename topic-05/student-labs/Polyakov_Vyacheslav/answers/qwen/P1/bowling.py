class BowlingGame:
    """Represents a game of bowling and keeps track of the score."""

    def __init__(self) -> None:
        self.rolls: list[int] = []
        self.frame: int = 1
        self.throw: int = 1
        self.pins_remaining: int = 10
        self.game_over: bool = False

    def roll(self, pins: int) -> None:
        """Records a roll where `pins` pins are knocked down."""
        if type(pins) is not int:
            raise TypeError("Pins must be an integer")
        if self.game_over:
            raise ValueError("Cannot roll after the game is over")
        if not (0 <= pins <= 10):
            raise ValueError("Invalid number of pins")
        if pins > self.pins_remaining:
            raise ValueError("Not enough pins remaining")
            
        self.rolls.append(pins)
        self.pins_remaining -= pins
        
        if self.frame < 10:
            if self.throw == 1:
                if pins == 10:
                    self.frame += 1
                    self.throw = 1
                    self.pins_remaining = 10
                else:
                    self.throw = 2
            else:
                self.frame += 1
                self.throw = 1
                self.pins_remaining = 10
        else:
            if self.throw == 1:
                if pins == 10:
                    self.throw = 2
                    self.pins_remaining = 10
                else:
                    self.throw = 2
            elif self.throw == 2:
                if self.rolls[-2] == 10:
                    if pins == 10:
                        self.throw = 3
                        self.pins_remaining = 10
                    else:
                        self.throw = 3
                else:
                    if self.pins_remaining == 0:
                        self.throw = 3
                        self.pins_remaining = 10
                    else:
                        self.game_over = True
            elif self.throw == 3:
                self.game_over = True

    def score(self) -> int:
        """Returns the total score for the game."""
        if not self.game_over:
            raise ValueError("Cannot score an incomplete game")
        
        total = 0
        roll_idx = 0
        for frame in range(10):
            if frame < 9:
                if self.rolls[roll_idx] == 10:
                    total += 10 + self.rolls[roll_idx + 1] + self.rolls[roll_idx + 2]
                    roll_idx += 1
                elif self.rolls[roll_idx] + self.rolls[roll_idx + 1] == 10:
                    total += 10 + self.rolls[roll_idx + 2]
                    roll_idx += 2
                else:
                    total += self.rolls[roll_idx] + self.rolls[roll_idx + 1]
                    roll_idx += 2
            else:
                total += sum(self.rolls[roll_idx:])
                
        return total
