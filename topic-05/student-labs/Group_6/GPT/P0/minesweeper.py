def annotate(minefield: list[str]) -> list[str]:
    error_message = "The board is invalid with current input."

    # Проверяем, что поле прямоугольное и содержит только пробелы и мины.
    if not isinstance(minefield, (list, tuple)):
        raise ValueError(error_message)

    if any(not isinstance(row, str) for row in minefield):
        raise ValueError(error_message)

    if minefield and any(len(row) != len(minefield[0]) for row in minefield):
        raise ValueError(error_message)

    if any(cell not in " *" for row in minefield for cell in row):
        raise ValueError(error_message)

    height = len(minefield)
    width = len(minefield[0]) if height else 0
    result = []

    for row in range(height):
        new_row = []

        for col in range(width):
            if minefield[row][col] == "*":
                new_row.append("*")
                continue

            mines = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue

                    neighbor_row = row + dr
                    neighbor_col = col + dc

                    if (
                        0 <= neighbor_row < height
                        and 0 <= neighbor_col < width
                        and minefield[neighbor_row][neighbor_col] == "*"
                    ):
                        mines += 1

            new_row.append(str(mines) if mines else " ")

        result.append("".join(new_row))

    return result