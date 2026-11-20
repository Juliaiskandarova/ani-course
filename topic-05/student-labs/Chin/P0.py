class BowlingGame:
    def __init__(self) -> None:
        self._frames: list[list[int]] = [[] for _ in range(10)]
        self._frame_index = 0

    def roll(self, pins: int) -> None:
        if self._frame_index == 10:
            raise ValueError("Игра уже завершена.")
        if type(pins) is not int or not 0 <= pins <= 10:
            raise ValueError("Количество сбитых кеглей должно быть целым числом от 0 до 10.")

        frame = self._frames[self._frame_index]
        last_frame = self._frame_index == 9
        standing = 10

        if len(frame) == 1 and frame[0] < 10:
            standing = 10 - frame[0]
        elif len(frame) == 2 and frame[0] == 10:
            # После страйка в десятом фрейме второй бросок делается
            # по полному набору, а третий — по оставшимся кеглям.
            if frame[1] < 10:
                standing = 10 - frame[1]

        if pins > standing:
            raise ValueError(f"Перед броском осталось только {standing} кеглей.")

        frame.append(pins)

        if last_frame:
            if len(frame) == 3 or (len(frame) == 2 and sum(frame) < 10):
                self._frame_index += 1
        elif frame[0] == 10 or len(frame) == 2:
            self._frame_index += 1

    def score(self) -> int:
        if self._frame_index < 10:
            raise ValueError("Итоговый счёт доступен после завершения игры.")

        rolls = [pins for frame in self._frames for pins in frame]
        total = sum(self._frames[-1])
        position = 0

        for frame in self._frames[:-1]:
            total += sum(frame)

            if frame[0] == 10:
                total += rolls[position + 1] + rolls[position + 2]
            elif sum(frame) == 10:
                total += rolls[position + 2]

            position += len(frame)

        return total

game = BowlingGame()
for _ in range(12):
    game.roll(10)

assert game.score() == 300