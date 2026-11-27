def annotate(minefield: list[str]) -> list[str]:
    """Return the minefield with adjacent mine counts added to empty squares."""
    error_message = "The board is invalid with current input."

    if not isinstance(minefield, list) or any(
        not isinstance(row, str) for row in minefield
    ):
        raise ValueError(error_message)

    if minefield and any(len(row) != len(minefield[0]) for row in minefield):
        raise ValueError(error_message)

    if any(square not in " *" for row in minefield for square in row):
        raise ValueError(error_message)

    height = len(minefield)
    width = len(minefield[0]) if height else 0
    result: list[str] = []

    for row in range(height):
        annotated_row: list[str] = []
        for column in range(width):
            if minefield[row][column] == "*":
                annotated_row.append("*")
                continue

            adjacent_mines = sum(
                1
                for neighbor_row in range(max(0, row - 1), min(height, row + 2))
                for neighbor_column in range(
                    max(0, column - 1), min(width, column + 2)
                )
                if minefield[neighbor_row][neighbor_column] == "*"
            )
            annotated_row.append(str(adjacent_mines) if adjacent_mines else " ")

        result.append("".join(annotated_row))

    return result