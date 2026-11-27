def annotate(minefield: list[str]) -> list[str]:
    """Return the minefield with adjacent mine counts added to empty squares.

    Args:
        minefield: A rectangular board where each row contains only ' ' and '*'.

    Returns:
        A new board with empty squares replaced by adjacent mine counts where
        applicable.

    Raises:
        ValueError: If the board is not rectangular or contains invalid characters.
    """
    error_message = "The board is invalid with current input."

    if not isinstance(minefield, list):
        raise ValueError(error_message)

    width: int | None = None

    for row in minefield:
        if not isinstance(row, str):
            raise ValueError(error_message)

        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ValueError(error_message)

        if any(char not in " *" for char in row):
            raise ValueError(error_message)

    if not minefield:
        return []

    assert width is not None

    height = len(minefield)
    result: list[str] = []

    for row_index in range(height):
        new_row: list[str] = []

        for column_index in range(width):
            if minefield[row_index][column_index] == "*":
                new_row.append("*")
                continue

            adjacent_mines = 0

            for row_offset in (-1, 0, 1):
                for column_offset in (-1, 0, 1):
                    if row_offset == 0 and column_offset == 0:
                        continue

                    neighbor_row = row_index + row_offset
                    neighbor_column = column_index + column_offset

                    if (
                        0 <= neighbor_row < height
                        and 0 <= neighbor_column < width
                        and minefield[neighbor_row][neighbor_column] == "*"
                    ):
                        adjacent_mines += 1

            new_row.append(str(adjacent_mines) if adjacent_mines else " ")

        result.append("".join(new_row))

    return result