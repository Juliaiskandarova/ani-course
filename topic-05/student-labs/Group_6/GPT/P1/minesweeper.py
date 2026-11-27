def annotate(minefield: list[str]) -> list[str]:
    """Add adjacent-mine counts to each empty square in a Minesweeper board."""
    invalid_message = "The board is invalid with current input."

    if not isinstance(minefield, list) or any(
        not isinstance(row, str) for row in minefield
    ):
        raise ValueError(invalid_message)

    if not minefield:
        return []

    width = len(minefield[0])
    if any(
        len(row) != width or any(square not in " *" for square in row)
        for row in minefield
    ):
        raise ValueError(invalid_message)

    height = len(minefield)
    result: list[str] = []

    for row_index, row in enumerate(minefield):
        annotated_row: list[str] = []

        for column_index, square in enumerate(row):
            if square == "*":
                annotated_row.append("*")
                continue

            adjacent_mines = sum(
                1
                for neighbor_row in range(max(0, row_index - 1), min(height, row_index + 2))
                for neighbor_column in range(
                    max(0, column_index - 1), min(width, column_index + 2)
                )
                if minefield[neighbor_row][neighbor_column] == "*"
            )
            annotated_row.append(str(adjacent_mines) if adjacent_mines else " ")

        result.append("".join(annotated_row))

    return result