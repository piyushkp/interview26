MOVES = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}


def solution(
    maze: list[str], actions: list[tuple[int, str]], end_time: int
) -> list[str]:
    board = [list(row) for row in maze]
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == "o":
                robot_row, robot_col = row, col
                break
        else:
            continue
        break

    actions = sorted(actions)
    action_index = 0
    direction = None

    for time in range(end_time):
        if action_index < len(actions) and actions[action_index][0] == time:
            direction = actions[action_index][1]
            action_index += 1

        if direction is None:
            continue

        row_change, col_change = MOVES[direction]
        new_row = robot_row + row_change
        new_col = robot_col + col_change

        if board[new_row][new_col] == " ":
            board[robot_row][robot_col] = " "
            board[new_row][new_col] = "o"
            robot_row, robot_col = new_row, new_col

    return ["".join(row) for row in board]


if __name__ == "__main__":
    example = [
        "-------",
        "|     |",
        "|     |",
        "| o   |",
        "-------",
    ]
    expected = [
        "-------",
        "|    o|",
        "|     |",
        "|     |",
        "-------",
    ]
    result = solution(example, [(0, "UP"), (3, "RIGHT")], 10)
    assert result == expected
    assert example[3] == "| o   |"
    print("\n".join(result))