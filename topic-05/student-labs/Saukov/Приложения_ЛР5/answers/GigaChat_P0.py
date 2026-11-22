class BowlingGame:
    def __init__(self):
        self.rolls = []
        self.current_frame = 1
        self.frame_rolls = 0

    def roll(self, pins: int):
        if pins < 0 or pins > 10:
            raise ValueError("Количество сбитых кеглей должно быть от 0 до 10")
        
        # Проверка, не превышено ли количество фреймов
        if self.current_frame > 10:
            raise ValueError("Игра уже завершена, нельзя делать дополнительные броски")
        
        self.rolls.append(pins)
        self.frame_rolls += 1
        
        # Переход к следующему фрейму, если необходимо
        if self.current_frame < 10:
            if pins == 10 or self.frame_rolls == 2:
                self.current_frame += 1
                self.frame_rolls = 0
        else:
            # В 10-м фрейме разрешены дополнительные броски при strike или spare
            if self.frame_rolls == 3 or (self.frame_rolls == 2 and pins < 10):
                self.current_frame += 1

    def score(self):
        if self.current_frame <= 10:
            raise ValueError("Игра еще не завершена")
        
        total_score = 0
        roll_index = 0
        
        for frame in range(10):
            if self.rolls[roll_index] == 10:  # Strike
                total_score += 10 + self.rolls[roll_index + 1] + self.rolls[roll_index + 2]
                roll_index += 1
            elif self.rolls[roll_index] + self.rolls[roll_index + 1] == 10:  # Spare
                total_score += 10 + self.rolls[roll_index + 2]
                roll_index += 2
            else:  # Открытый фрейм
                total_score += self.rolls[roll_index] + self.rolls[roll_index + 1]
                roll_index += 2
        
        return total_score