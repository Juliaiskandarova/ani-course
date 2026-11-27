"""Minesweeper: annotate empty squares with the number of adjacent mines."""

INVALID = "The board is invalid with current input."


def annotate(minefield):
    """Return a new board where each empty square holds its adjacent-mine count.

    A square with no adjacent mines stays ' '; mines ('*') are left untouched.
    Raises ValueError if rows differ in length or contain characters other
    than ' ' and '*'.
    """
    if not minefield:
        return []

    height = len(minefield)
    width = len(minefield[0])

    # --- validation -----------------------------------------------------
    for row in minefield:
        if len(row) != width or any(ch not in " *" for ch in row):
            raise ValueError(INVALID)

    # --- annotation -----------------------------------------------------
    result = []
    for r in range(height):
        line = []
        for c in range(width):
            if minefield[r][c] == "*":
                line.append("*")
                continue

            mines = sum(
                minefield[rr][cc] == "*"
                for rr in range(max(0, r - 1), min(height, r + 2))
                for cc in range(max(0, c - 1), min(width, c + 2))
                if (rr, cc) != (r, c)
            )
            line.append(str(mines) if mines else " ")
        result.append("".join(line))

    return result