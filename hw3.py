from typing import List


def tic_tac_toe_checker(board: List[List]) -> str:
    # проверка строк и столбцов
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "-":
            return f"{board[i][0]} wins!"
        if board[0][i] == board[1][i] == board[2][i] != "-":
            return f"{board[0][i]} wins!"

    # проверка диагоналей
    if board[0][0] == board[1][1] == board[2][2] != "-":
        return f"{board[0][0]} wins!"
    if board[0][2] == board[1][1] == board[2][0] != "-":
        return f"{board[0][2]} wins!"

    # проверка на наличие незаполненных ячеек
    if any("-" in row for row in board):
        return "unfinished"

    # если нет победителя и поле заполнено - ничья
    return "draw!"


# пример
board1 = [["-", "-", "o"],
          ["-", "x", "o"],
          ["x", "o", "x"]]
print(tic_tac_toe_checker(board1))  # unfinished

board2 = [["-", "-", "o"],
          ["-", "o", "o"],
          ["x", "x", "x"]]
print(tic_tac_toe_checker(board2))  # x wins!

board3 = [["-", "-", "o"],
          ["-", "o", "o"],
          ["o", "x", "x"]]
print(tic_tac_toe_checker(board3))  # o wins!

board4 = [["o", "x", "o"],
          ["x", "o", "o"],
          ["x", "o", "x"]]
print(tic_tac_toe_checker(board4))  # draw!
