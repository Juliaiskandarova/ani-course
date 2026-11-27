def annotate(board):
    if not board:
        return []

    width = len(board[0])

    # Проверка на прямоугольность доски
    if any(len(row) != width for row in board):
        raise ValueError("The board is invalid with current input.")

    # Проверка допустимых символов
    if any(ch not in " *" for row in board for ch in row):
        raise ValueError("The board is invalid with current input.")

    height = len(board)
    result = []

    for r in range(height):
        new_row = []

        for c in range(width):
            if board[r][c] == "*":
                new_row.append("*")
                continue

            mines = 0

            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue

                    nr, nc = r + dr, c + dc

                    if (
                        0 <= nr < height
                        and 0 <= nc < width
                        and board[nr][nc] == "*"
                    ):
                        mines += 1

            new_row.append(str(mines) if mines > 0 else " ")

        result.append("".join(new_row))

    return result