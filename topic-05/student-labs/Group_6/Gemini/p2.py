def annotate(minefield: list[str]) -> list[str]:
    """Count adjacent mines for each empty square on a Minesweeper board.

    Args:
        minefield: A list of strings representing rows of the board, where
            ' ' is an empty square and '*' is a mine.

    Returns:
        A list of strings with empty squares replaced by the count of
        adjacent mines (1-8), or left as ' ' if there are none.

    Raises:
        ValueError: If the board rows have unequal lengths or contain
            characters other than ' ' and '*'.
    """
    if not minefield:
        return []

    rows = len(minefield)
    cols = len(minefield[0])

    for row in minefield:
        if len(row) != cols:
            raise ValueError("The board is invalid with current input.")
        for cell in row:
            if cell not in (" ", "*"):
                raise ValueError("The board is invalid with current input.")

    result: list[str] = []
    for r in range(rows):
        row_chars: list[str] = []
        for c in range(cols):
            if minefield[r][c] == "*":
                row_chars.append("*")
            else:
                count = sum(
                    1
                    for dr in (-1, 0, 1)
                    for dc in (-1, 0, 1)
                    if (dr != 0 or dc != 0)
                    and 0 <= r + dr < rows
                    and 0 <= c + dc < cols
                    and minefield[r + dr][c + dc] == "*"
                )
                row_chars.append(str(count) if count > 0 else " ")
        result.append("".join(row_chars))

    return result
