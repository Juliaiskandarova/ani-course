def annotate(minefield):
    """Annotate a Minesweeper board with mine counts.
    
    Args:
        minefield: A list of strings representing the board.
                   Each string contains only ' ' (empty) or '*' (mine).
    
    Returns:
        A new list of strings with empty squares replaced by adjacent mine counts.
    
    Raises:
        ValueError: If the input is malformed.
    """
    # Validate input type
    if not isinstance(minefield, list):
        raise ValueError("The board is invalid with current input.")
    
    # Handle empty board
    if len(minefield) == 0:
        return []
    
    # Validate all rows are strings
    for row in minefield:
        if not isinstance(row, str):
            raise ValueError("The board is invalid with current input.")
    
    # Validate all rows have the same length
    row_length = len(minefield[0])
    for row in minefield:
        if len(row) != row_length:
            raise ValueError("The board is invalid with current input.")
    
    # Validate only valid characters (space and mine)
    for row in minefield:
        for char in row:
            if char not in (' ', '*'):
                raise ValueError("The board is invalid with current input.")
    
    # Process the board
    rows = len(minefield)
    cols = row_length
    result = []
    
    for r in range(rows):
        new_row = []
        for c in range(cols):
            if minefield[r][c] == '*':
                new_row.append('*')
            else:
                # Count adjacent mines in all 8 directions
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if minefield[nr][nc] == '*':
                                count += 1
                
                if count > 0:
                    new_row.append(str(count))
                else:
                    new_row.append(' ')
        
        result.append(''.join(new_row))
    
    return result