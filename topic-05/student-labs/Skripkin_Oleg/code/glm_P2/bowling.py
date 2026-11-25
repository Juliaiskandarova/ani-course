class BowlingGame:
    """
    A class to keep track of the score of a game of bowling.
    """

    def __init__(self) -> None:
        """Initialize a new BowlingGame instance."""
        self.rolls: list[int] = []

    def roll(self, pins: int) -> None:
        """
        Called each time the player rolls a ball.
        
        Args:
            pins: The number of pins knocked down in the roll.

        Raises:
            ValueError: If the input is invalid or the game is already over.
        """
        if not isinstance(pins, int) or isinstance(pins, bool):
            raise ValueError("Invalid roll: pins must be an integer.")
        if pins < 0 or pins > 10:
            raise ValueError("Invalid roll: pins must be between 0 and 10.")
        
        frames_checked = 0
        current_frame_rolls = 0
        current_frame_pins = 0
        current_frame_strike = False
        
        for roll_idx, p in enumerate(self.rolls):
            if frames_checked < 9:
                if current_frame_strike:
                    frames_checked += 1
                    current_frame_strike = False
                    current_frame_rolls = 0
                    current_frame_pins = p
                    if p == 10:
                        current_frame_strike = True
                    else:
                        current_frame_rolls = 1
                else:
                    current_frame_pins += p
                    current_frame_rolls += 1
                    if current_frame_rolls == 1 and p == 10:
                        current_frame_strike = True
                    elif current_frame_rolls == 2:
                        frames_checked += 1
                        current_frame_rolls = 0
                        current_frame_pins = 0
            else:  # 10th frame
                if current_frame_rolls == 0:
                    current_frame_pins = p
                    current_frame_rolls = 1
                    current_frame_strike = (p == 10)
                elif current_frame_rolls == 1:
                    if current_frame_strike:
                        current_frame_pins = p
                        current_frame_rolls = 2
                        current_frame_strike = (p == 10)
                    else:
                        if current_frame_pins + p > 10:
                            raise ValueError("Invalid roll: cannot knock down more than 10 pins in a frame.")
                        current_frame_pins += p
                        current_frame_rolls = 2
                elif current_frame_rolls == 2:
                    if current_frame_pins == 10:
                        current_frame_pins = p
                        current_frame_rolls = 3
                    else:
                        if current_frame_pins + p > 10:
                            raise ValueError("Invalid roll: cannot knock down more than 10 pins in a frame.")
                        current_frame_pins += p
                        current_frame_rolls = 3
                else:  # 3
                    raise ValueError("Cannot roll after the game is over.")

        if frames_checked < 9:
            if current_frame_strike:
                self.rolls.append(pins)
                return
            
            current_frame_pins += pins
            current_frame_rolls += 1
            if current_frame_pins > 10:
                raise ValueError("Invalid roll: cannot knock down more than 10 pins in a frame.")
            if current_frame_rolls == 2:
                frames_checked += 1
            
            if frames_checked == 10:
                raise ValueError("Cannot roll after the game is over.")
            self.rolls.append(pins)
        else:  # 10th frame
            if current_frame_rolls == 0:
                self.rolls.append(pins)
            elif current_frame_rolls == 1:
                if current_frame_strike:
                    self.rolls.append(pins)
                else:
                    if current_frame_pins + pins > 10:
                        raise ValueError("Invalid roll: cannot knock down more than 10 pins in a frame.")
                    self.rolls.append(pins)
            elif current_frame_rolls == 2:
                if current_frame_strike and current_frame_pins == 10:
                    if pins > 10:
                        raise ValueError("Invalid roll: pins must be between 0 and 10.")
                    self.rolls.append(pins)
                elif not current_frame_strike and current_frame_pins == 10:
                    if current_frame_pins + pins > 10:
                        raise ValueError("Invalid roll: cannot knock down more than 10 pins in a frame.")
                    self.rolls.append(pins)
                else:
                    raise ValueError("Cannot roll after the game is over.")
            else:
                raise ValueError("Cannot roll after the game is over.")

    def score(self) -> int:
        """
        Called only at the very end of the game. It returns the total score for that game.

        Returns:
            The total score for the game.

        Raises:
            ValueError: If the game is not complete.
        """
        if len(self.rolls) == 0:
            raise ValueError("Game is not complete.")
        
        frames_checked = 0
        current_frame_rolls = 0
        current_frame_pins = 0
        current_frame_strike = False
        game_complete = False
        
        for p in self.rolls:
            if frames_checked < 9:
                if current_frame_strike:
                    frames_checked += 1
                    current_frame_strike = False
                    current_frame_rolls = 0
                    current_frame_pins = p
                    if p == 10:
                        current_frame_strike = True
                    else:
                        current_frame_rolls = 1
                else:
                    current_frame_pins += p
                    current_frame_rolls += 1
                    if current_frame_rolls == 1 and p == 10:
                        current_frame_strike = True
                    elif current_frame_rolls == 2:
                        frames_checked += 1
                        current_frame_rolls = 0
                        current_frame_pins = 0
            else:
                if current_frame_rolls == 0:
                    current_frame_pins = p
                    current_frame_rolls = 1
                    current_frame_strike = (p == 10)
                elif current_frame_rolls == 1:
                    if current_frame_strike:
                        current_frame_pins = p
                        current_frame_rolls = 2
                        current_frame_strike = (p == 10)
                    else:
                        current_frame_pins += p
                        current_frame_rolls = 2
                elif current_frame_rolls == 2:
                    if current_frame_pins == 10:
                        current_frame_pins = p
                        current_frame_rolls = 3
                    else:
                        current_frame_pins += p
                        current_frame_rolls = 3
                else:
                    game_complete = True
                    break
        
        if frames_checked < 9:
            if current_frame_strike or current_frame_rolls == 2:
                frames_checked += 1
                
        if frames_checked == 10 and not game_complete:
            if current_frame_rolls == 2 and current_frame_pins < 10:
                game_complete = True
            
        if not game_complete:
            raise ValueError("Game is not complete.")
        
        total_score = 0
        roll_index = 0
        
        for _ in range(10):
            if self.rolls[roll_index] == 10:
                total_score += 10 + self.rolls[roll_index + 1] + self.rolls[roll_index + 2]
                roll_index += 1
            elif self.rolls[roll_index] + self.rolls[roll_index + 1] == 10:
                total_score += 10 + self.rolls[roll_index + 2]
                roll_index += 2
            else:
                total_score += self.rolls[roll_index] + self.rolls[roll_index + 1]
                roll_index += 2
                
        return total_score
