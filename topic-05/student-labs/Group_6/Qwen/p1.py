def annotate(minefield):
    """Annotate a Minesweeper board with mine counts for empty squares.

    Args:
        minefield: A list of strings representing the board.
                   Empty squares are ' ', mines are '*'.

    Returns:
        A new list of strings with empty squares replaced by adjacent
        mine counts (1-8), or left as ' ' if no adjacent mines.

    Raises:
        ValueError: If the input board is malformed.
    """
    if not isinstance(minefield, list):
        raise ValueError("The board is invalid with current input.")

    if not minefield:
        return []

    row_length = len(minefield[0])

    for row in minefield:
        if not isinstance(row, str):
            raise ValueError("The board is invalid with current input.")
        if len(row) != row_length:
            raise ValueError("The board is invalid with current input.")
        for char in row:
            if char not in (' ', '*'):
                raise ValueError("The board is invalid with current input.")

    rows = len(minefield)
    cols = row_length
    result = []

    for row_idx in range(rows):
        annotated_row = []
        for col_idx in range(cols):
            if minefield[row_idx][col_idx] == '*':
                annotated_row.append('*')
            else:
                mine_count = 0
                for delta_row in (-1, 0, 1):
                    for delta_col in (-1, 0, 1):
                        if delta_row == 0 and delta_col == 0:
                            continue
                        neighbor_row = row_idx + delta_row
                        neighbor_col = col_idx + delta_col
                        if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols:
                            if minefield[neighbor_row][neighbor_col] == '*':
                                mine_count += 1
                if mine_count == 0:
                    annotated_row.append(' ')
                else:
                    annotated_row.append(str(mine_count))
        result.append(''.join(annotated_row))

    return result