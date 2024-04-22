import uuid

from authenticity import db, findingUser

turn_order = db["turn_order"]
game_boards = db["game_boards"]

places = {"1": (0, 0), "2": (0, 1), "3": (0, 2), "4": (1, 0), "5": (1, 1), "6": (1, 2), "7": (2, 0), "8": (2, 1),
          "9": (2, 2)}


# Will return a new empty grid object. The 0's on this grid will be filled with the name of the player,
# and if the user's name appears three time consecutively (vert, horiz, diag) it determine a win for that player.
# grid will be stored in the database for use.
def start_new_game(token):
    player = findingUser(token)
    grid = [['0', '0', '0'], ['0', '0', '0'], ['0', '0', '0']]
    available_game = game_boards.find_one({"status": "waiting"})

    if available_game:
        players = available_game.get("players", []) + [player]
        game_boards.update_one({'id': available_game['id']}, {'$set': {'status': 'ongoing', 'players': players}})
        return available_game['id']
    else:
        game_id = str(uuid.uuid4())
        game_boards.insert_one({"id": game_id, "board": grid, "status": "waiting", "players": [player], "current_turn": player})
        return game_id


# Will be called by "move()" after each move the respective player makes. Will return "Draw" if no winner is found, but
# all spaces on the grid AREN'T a '0'. Will return "Win" if a matching pattern is found. If neither and the game is
# still ongoing, will return "Continue"
def check_winner(name, boardID):
    game_data = game_boards.find_one({"id": boardID})
    board = game_data["board"]
    print("----------------------")
    print(board)
    print("----------------------")
    if "0" not in board[0] and "0" not in board[1] and '0' not in board[2]:
        game_boards.delete_one({"id": boardID})
        return "Tie"

    if (board[0][0] == board[1][1] == board[2][2] and board[0][0] != '0') or \
            (board[0][2] == board[1][1] == board[2][0] and board[0][2] != '0'):
        game_boards.delete_one({"id": boardID})
        return name + " Wins"

    for row in board:
        if row[0] == row[1] == row[2] and row[0] != '0':
            game_boards.delete_one({"id": boardID})
            return name + " Wins"

    col = 0
    while col < 3:
        if board[0][col] == board[1][col] == board[2][col] and board[2][col] != '0':
            game_boards.delete_one({"id": boardID})
            return name + " Wins"

    return "Continue"


# Include the name of the current player making a move. Will update the grid if the chosen position is available,
# and store that updated grid in the database for the front-end to retrieve. (Most likely) board parameter will be
# removed and replaced with retrieving the board from the database.
def move(boardID, place, token):
    game_data = game_boards.find_one({"id": boardID})
    if not game_data:
        return "Game not found"

    board = game_data["board"]
    name = findingUser(token)
    position = places.get(place)

    if board[position[0]][position[1]] != '0':
        return "Position already taken"

    if name != game_data["current_turn"]:
        return "It's not your turn"

    board[position[0]][position[1]] = name

    next_player_index = (game_data["players"].index(name) + 1) % len(game_data["players"])
    next_player = game_data["players"][next_player_index]

    game_boards.update_one({'id': boardID}, {'$set': {'board': board, "current_turn": next_player}})

    result = check_winner(name, boardID)
    if result == "Tie":
        return "Tie"
    elif result == "Win":
        return "Win"
    else:
        return "Continue"

