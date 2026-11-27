def annotate(minefield: list[str]) -> list[str]:
    """Calculate the number of adjacent mines for each empty square on a Minesweeper board.

    Args:
        minefield: A list of strings representing the rows of the board, where ' ' denotes
            an empty square and '*' denotes a mine.

    Returns:
        A list of strings representing the annotated board, where each empty square with
        at least one adjacent mine is replaced by the count of adjacent mines.

    Raises:
        ValueError: If the board is not rectangular, contains invalid characters, or
            is not a valid list of strings.
    """
    if not isinstance(minefield, list) or any(
        not isinstance(row, str) for row in minefield
    ):
        raise ValueError("The board is invalid with current input.")

    if not minefield:
        return []

    rows = len(minefield)
    cols = len(minefield[0])

    for row in minefield:
        if len(row) != cols:
            raise ValueError("The board is invalid with current input.")
        if any(cell not in (" ", "*") for cell in row):
            raise ValueError("The board is invalid with current input.")

    result: list[str] = []
    for r in range(rows):
        new_row: list[str] = []
        for c in range(cols):
            if minefield[r][c] == "*":
                new_row.append("*")
                continue

            mine_count = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < rows
                        and 0 <= nc < cols
                        and minefield[nr][nc] == "*"
                    ):
                        mine_count += 1

            new_row.append(str(mine_count) if mine_count > 0 else " ")
        result.append("".join(new_row))

    return result


