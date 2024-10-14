BOARD_WIDTH = 10
BOARD_HEIGHT = 20


def print_board(board: list[list[int]]):
    for row in board:
        print("".join(['⬛' if cell == 1 else '⬜' for cell in row]))


def gravitate_row(board: list[list[int]], row: int):
    current_row = row
    for y in range(row + 1, BOARD_HEIGHT):
        empty = all(board[y][x] == 0 for x in range(BOARD_WIDTH))
        # if empty swap row with current row
        if empty:
            board[current_row], board[y] = board[y], board[current_row]
            current_row = y


def burn_lines(board: list[list[int]]):
    for y in range(BOARD_HEIGHT):
        full = all(board[y][x] == 1 for x in range(BOARD_WIDTH))
        if full:
            for x in range(BOARD_WIDTH):
                board[y][x] = 0

    for y in range(BOARD_HEIGHT -1, -1, -1):
        empty = all(board[y][x] == 0 for x in range(BOARD_WIDTH))
        if not empty:
            gravitate_row(board, y)


if __name__ == "__main__":
    board = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    print_board(board)
    burn_lines(board)
    print("After burning lines:")
    print_board(board)