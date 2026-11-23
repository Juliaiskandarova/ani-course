class BowlingGame:
    def __init__(self):
        self.rolls = []
        self.current_frame = 1
        self.throws_in_current_frame = []
        self.pins_standing = 10
        self.game_over = False

    def roll(self, pins: int) -> None:
        if self.game_over:
            raise ValueError("Cannot roll after the game is over.")
        if pins < 0 or pins > 10:
            raise ValueError("Pins must have a value from 0 to 10.")
        if pins > self.pins_standing:
            raise ValueError("Pin count exceeds number of standing pins.")
        
        self.rolls.append(pins)
        self.throws_in_current_frame.append(pins)
        self.pins_standing -= pins
        
        frame_over = False
        
        if self.current_frame < 10:
            # Frames 1-9
            if self.throws_in_current_frame[0] == 10:  # Strike
                frame_over = True
            elif len(self.throws_in_current_frame) == 2:
                frame_over = True
        else:
            # 10th Frame
            if len(self.throws_in_current_frame) == 1:
                frame_over = False
            elif len(self.throws_in_current_frame) == 2:
                if self.throws_in_current_frame[0] == 10:  # Strike on 1st ball
                    frame_over = False
                elif sum(self.throws_in_current_frame) == 10:  # Spare
                    frame_over = False
                else:  # Open frame
                    frame_over = True
            elif len(self.throws_in_current_frame) == 3:
                frame_over = True
        
        if frame_over:
            if self.current_frame == 10:
                self.game_over = True
            else:
                self.current_frame += 1
                self.throws_in_current_frame = []
                self.pins_standing = 10
        else:
            # Handle pin resets specifically for the 10th frame fill balls
            if self.current_frame == 10:
                if self.throws_in_current_frame[-1] == 10 or sum(self.throws_in_current_frame) == 10:
                    self.pins_standing = 10

    def score(self) -> int:
        if not self.game_over:
            raise ValueError("Cannot score a game that is not over.")
        
        total_score = 0
        roll_index = 0
        
        for _ in range(1, 11):
            if self.rolls[roll_index] == 10:  # Strike
                total_score += 10 + self.rolls[roll_index + 1] + self.rolls[roll_index + 2]
                roll_index += 1
            elif self.rolls[roll_index] + self.rolls[roll_index + 1] == 10:  # Spare
                total_score += 10 + self.rolls[roll_index + 2]
                roll_index += 2
            else:  # Open frame
                total_score += self.rolls[roll_index] + self.rolls[roll_index + 1]
                roll_index += 2
                
        return total_score
