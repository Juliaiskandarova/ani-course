def annotate(minefield):
    # Проверка на пустую доску (возвращаем пустой список, если строк нет)
    if not minefield:
        return []

    rows = len(minefield)
    cols = len(minefield[0])

    # Валидация: все строки должны быть одинаковой длины и содержать только ' ' или '*'
    for row in minefield:
        if len(row) != cols or any(cell not in (" ", "*") for cell in row):
            raise ValueError("The board is invalid with current input.")

    result = []

    # Проходим по каждой клетке поля
    for r in range(rows):
        new_row = []
        for c in range(cols):
            # Если в клетке мина, оставляем её без изменений
            if minefield[r][c] == "*":
                new_row.append("*")
                continue

            # Считаем количество мин в соседних 8 клетках
            mine_count = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    # Проверяем, что соседняя клетка не выходит за границы поля
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if minefield[nr][nc] == "*":
                            mine_count += 1

            # Если мин вокруг нет — оставляем пробел, иначе ставим цифру
            new_row.append(str(mine_count) if mine_count > 0 else " ")

        result.append("".join(new_row))

    return result


board = [
    " * * ",
    "  *  ",
    "  *  ",
    "     ",
]

annotated_board = annotate(board)
for line in annotated_board:
    # Заменяем пробелы на '·' только для наглядного вывода в консоль
    print(line.replace(" ", "·"))

