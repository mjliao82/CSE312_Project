
places = {"1": (0, 0), "2": (0, 1), "3": (0, 2), "4": (1, 0), "5": (1, 1), "6": (1, 2), "7": (2, 0), "8": (2, 1), "9": (2, 2)}


# Will return a new empty grid object. The 0's on this grid will be filled with the name of the player,
# and if the user's name appears three time consecutively (vert, horiz, diag) it determine a win for that player.
# grid will be stored in the database for use.
def start_new_game():
    grid = [['0', '0', '0'], ['0', '0', '0'], ['0', '0', '0']]
    return grid  # Substitute for storing in database, along with (possibly) an ID to represent the game.


# Will be called by "move()" after each move the respective player makes. Will return "Draw" if no winner is found, but
# all spaces on the grid AREN'T a '0'. Will return "Win" if a matching pattern is found. If neither and the game is
# still ongoing, will return "Continue"
def check_winner(name, board):
    return "Continue"

# Include the name of the current player making a move. Will update the grid if the chosen position is available,
# and store that updated grid in the database for the front-end to retrieve. (Most likely) board parameter will be
# removed and replaced with retrieving the board from the database.
def move(board, place, name):
    position = places[place]
    if board.grid[position[0], position[1]] == '0':
        board.grid[position[0], position[1]] = name
    if check_winner(name, board) == "Tie":
        return "Tie"
    elif check_winner(name, board) == "Win":
        return "Win"
    else:
        return "Continue"




