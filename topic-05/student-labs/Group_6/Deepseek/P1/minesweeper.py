from typing import List

def annotate(minefield: List[str]) -> List[str]:
    """Add adjacent mine counts to empty squares in a completed Minesweeper board.

    Args:
        minefield: A rectangular board represented as a list of strings, where
            each character is either an empty square (' ') or a mine ('*').

    Returns:
        A new board with empty squares replaced by the number of adjacent mines,
        or left as ' ' when there are no adjacent mines.

    Raises:
        ValueError: If the board is not rectangular or contains invalid characters.
    """
    error_message = "The board is invalid with current input."

    if not isinstance(minefield, list):
        raise ValueError(error_message)

    if not minefield:
        return []

    width = None
    for row in minefield:
        if not isinstance(row, str):
            raise ValueError(error_message)
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ValueError(error_message)
        if any(ch not in (" ", "*") for ch in row):
            raise ValueError(error_message)

    height = len(minefield)
    result: List[List[str]] = [list(row) for row in minefield]

    for r in range(height):
        for c in range(width):
            if minefield[r][c] == "*":
                continue

            mine_count = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        if minefield[nr][nc] == "*":
                            mine_count += 1

            if mine_count:
                result[r][c] = str(mine_count)

    return ["".join(row) for row in result]
