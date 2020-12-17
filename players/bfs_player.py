from advance_model import *
from utils import *
import time


class myPlayer(AdvancePlayer):

    def __init__(self, _id):
        super().__init__(_id)

    def SelectMove(self, moves, game_state):
        # Global game start
        # All debugPoint is used to debug
        # If the game is the first round
        if self.IsFirstRound(game_state) == True:
            print("debugPoint0")
            # If I am the first move
            if self.IsMyFirstMove(game_state) == True:
                print("debugPoint1")
                # Use the naive method
                best_move = self.SelectFirstMove(game_state)
                print("debugPoint2")
                return best_move

            else:  # Not my first move, take bfs, -99999 is for initialize
                print("debugPoint3")
                max = -99999
                # Get actions, it is a (state, move) tuple
                actions = self.BFS(game_state)

                print("debugPoint4")
                # If the actions is empty
                if actions == []:
                    best_move = self.SelectFirstMove(game_state)
                    print("debugPoint5")
                    return best_move
                else:
                    print("debugPoint6")
                    # For all the actions obtained by the BFS traversal above, calculate the score. 
                    # If it is higher than the initial defined max score, then choose this new good state and move
                    for state, move, path in actions:
                        print("debugPoint7")
                        if self.CalculateScore(state) > max:
                            print("debugPoint8")
                            max = self.CalculateScore(state)
                            best_move = path[0][1]
                            print("debugPoint9")
                    # After traversing all the actions, return the best one just now
                    return best_move

        else:  # Not the first round of the whole game, the same as the above process
            print("debugPoint10")
            # If I am the first move
            if self.IsMyFirstMove(game_state) == True:
                best_move = self.SelectFirstMove(game_state)
                print("debugPoint11")
                return best_move

            else:  # Not my first move
                print("debugPoint12")
                max = -99999
                actions = self.BFS(game_state)
                print("debugPoint13")
                if actions == []:
                    best_move = self.SelectFirstMove(game_state)
                    print("debugPoint14")
                    return best_move
                else:
                    print("debugPoint15")
                    for state, move, path in actions:
                        print("debugPoint16")
                        if self.CalculateScore(state) > max:
                            print("debugPoint17")
                            max = self.CalculateScore(state)
                            best_move = path[0][1]
                            print("debugPoint18")
                    return best_move

    # If the chess board on the right is empty, it is the first round of whole game
    def IsFirstRound(self, game_state):
        if (game_state.players[self.id].grid_state == 0).all():
            print("This is the first round of all game.")
            return True
        else:
            return False

    # If the center is empty, it means that I am the first on to pick tiles
    def IsMyFirstMove(self, game_state):
        if game_state.centre_pool.total == 0:
            print("Center pool is 0.")
            print("I am the first to choose.")
            return True
        else:
            return False

    # Calculate the state score
    def CalculateScore(self, game_state):
        current_state_score = game_state.players[self.id].ScoreRound()[0]
        return current_state_score

    # The func has been completed, rewritten ExecuteMove(), enter a state and move, it will return a new newstate
    def GenerateNewState(self, game_state, move):
        new_state = copy.deepcopy(game_state)

        # The player is taking tiles from the centre
        if move[0] == Move.TAKE_FROM_CENTRE:
            tg = move[2]

            if not new_state.first_player_taken:
                new_state.players[self.id].GiveFirstPlayerToken()
                new_state.first_player_taken = True
                new_state.next_first_player = self.id

            if tg.num_to_floor_line > 0:
                ttf = []
                for i in range(tg.num_to_floor_line):
                    ttf.append(tg.tile_type)
                new_state.players[self.id].AddToFloor(ttf)
                new_state.bag_used.extend(ttf)

            if tg.num_to_pattern_line > 0:
                new_state.players[self.id].AddToPatternLine(tg.pattern_line_dest,
                                                            tg.num_to_pattern_line, tg.tile_type)

            # Remove tiles from the centre
            new_state.centre_pool.RemoveTiles(tg.number, tg.tile_type)

        elif move[0] == Move.TAKE_FROM_FACTORY:
            tg = move[2]
            if tg.num_to_floor_line > 0:
                ttf = []
                for i in range(tg.num_to_floor_line):
                    ttf.append(tg.tile_type)
                new_state.players[self.id].AddToFloor(ttf)
                new_state.bag_used.extend(ttf)

            if tg.num_to_pattern_line > 0:
                new_state.players[self.id].AddToPatternLine(tg.pattern_line_dest,
                                                            tg.num_to_pattern_line, tg.tile_type)

            # Remove tiles from the factory display
            fid = move[1]
            fac = new_state.factories[fid]
            fac.RemoveTiles(tg.number, tg.tile_type)

            # All remaining tiles on the factory display go into the
            # centre!
            for tile in Tile:
                num_on_fd = fac.tiles[tile]
                if num_on_fd > 0:
                    new_state.centre_pool.AddTiles(num_on_fd, tile)
                    fac.RemoveTiles(num_on_fd, tile)

        return new_state

    # Naive search for first move
    def SelectFirstMove(self, game_state):
        best_move = None
        most_to_line = -1
        corr_to_floor = 0
        moves = game_state.players[self.id].GetAvailableMoves(game_state)
        perfect_moves = self.FliterMove(game_state)
        if perfect_moves != []:
            for mid, fid, tgrab in perfect_moves:

                if most_to_line == -1:
                    best_move = (mid, fid, tgrab)
                    most_to_line = tgrab.num_to_pattern_line
                    corr_to_floor = tgrab.num_to_floor_line
                    continue

                if tgrab.num_to_pattern_line > most_to_line:
                    best_move = (mid, fid, tgrab)
                    most_to_line = tgrab.num_to_pattern_line
                    corr_to_floor = tgrab.num_to_floor_line

                elif tgrab.num_to_pattern_line == most_to_line and \
                        tgrab.num_to_pattern_line < corr_to_floor:
                    best_move = (mid, fid, tgrab)
                    most_to_line = tgrab.num_to_pattern_line
                    corr_to_floor = tgrab.num_to_floor_line
            return best_move
        else:
            for mid, fid, tgrab in moves:

                if most_to_line == -1:
                    best_move = (mid, fid, tgrab)
                    most_to_line = tgrab.num_to_pattern_line
                    corr_to_floor = tgrab.num_to_floor_line
                    continue

                if tgrab.num_to_pattern_line > most_to_line:
                    best_move = (mid, fid, tgrab)
                    most_to_line = tgrab.num_to_pattern_line
                    corr_to_floor = tgrab.num_to_floor_line

                elif tgrab.num_to_pattern_line == most_to_line and \
                        tgrab.num_to_pattern_line < corr_to_floor:
                    best_move = (mid, fid, tgrab)
                    most_to_line = tgrab.num_to_pattern_line
                    corr_to_floor = tgrab.num_to_floor_line
            return best_move

    # Filter the moves to get perfectmoves that fill the patternline perfectly and don't put in the floorline
    def FliterMove(self, game_state):

        moves = game_state.players[self.id].GetAvailableMoves(game_state)
        perfect_moves = []
        pattern_lines_number = game_state.players[self.id].lines_number
        pattern_lines_tile = game_state.players[self.id].lines_tile

        for mid, fid, tgrab in moves:
            # If the pattern of the line to be put is empty, I have not missed it
            if pattern_lines_tile[tgrab.pattern_line_dest] == -1:
                # Then, no matter what color, just the move that can be filled, and the move can’t put anything in the floor
                if tgrab.num_to_pattern_line == tgrab.pattern_line_dest + 1 and tgrab.num_to_floor_line == 0:
                    perfect_moves.append((mid, fid, tgrab))
            else:  # If the line to be put has color
                # Then grab the current color, the move that can be filled, and the move can't put things into the floor
                if pattern_lines_tile[
                    tgrab.pattern_line_dest] == tgrab.tile_type and tgrab.pattern_line_dest + 1 == tgrab.num_to_pattern_line + \
                        pattern_lines_number[tgrab.pattern_line_dest] and tgrab.num_to_floor_line == 0:
                    perfect_moves.append((mid, fid, tgrab))

        return perfect_moves

    def BFS(self, game_state):
        start_time = time.time()
        myQueue = Queue()
        myQueue.push((game_state, None, []))
        actions = []
        # When the queue is not empty
        while myQueue.isEmpty() != True:
            # Time out then break
            if time.time() - start_time > 0.9:
                return actions

            current_state, last_move, path = myQueue.pop()
            perfect_moves = self.FliterMove(current_state)

            # No perfect moves directly break
            if len(perfect_moves) == 0:
                print("No rest_move")
                return actions

            # For each candidate move in perfect moves
            for move in perfect_moves:
                # If time out break
                if time.time() - start_time > 0.9:
                    return actions
                # Generate a new subsequent node state
                new_state = self.GenerateNewState(current_state, move)
                # Push the new state into Queue
                myQueue.push((new_state, move, path + [(new_state, move)]))
                actions.append((new_state, move, path + [(new_state, move)]))
        return actions


# Copy the queue class of util.py from the pacman project of assignment1
class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."

    def __init__(self):
        self.list = []

    def push(self, item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0, item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0
