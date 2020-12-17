# Evaluation: (score_diff, score)
# Added rule based elements
# Also try to make dynamic depth

import sys
sys.path.append('players/Group36/')

# With alpha beta pruning
from advance_model import *
from utils import *

import time
import random

TIME_THRESHOLD = 0.9
UPPER_BOUND = 10  # upper bound for good moves number

class myPlayer(AdvancePlayer):
    def __init__(self,_id):
        super().__init__(_id)

    # Either I or my opponent have 5 tiles in any row, it will be the end the game
    def isEndOfGame(self, game_state):

        # My player state
        my_ps = game_state.players[self.id]
        # Opponent's player state
        oppo_ps = game_state.players[int(not self.id)]

        if my_ps.GetCompletedRows():
            return True
        if oppo_ps.GetCompletedRows():
            return True

        return False



    # Get the estimate excpetation after executing the move
    def sortMoves(self, candidates, game_state, plr_id):
        result = []
        for move in candidates:
            # Get the evaluation for each state
            score_pair = self.moveScore(move, game_state, plr_id)
            result.append((move, score_pair))
        return sorted(result, key = lambda x: x[1], reverse = True)

    # Get the evaluation for each state
    def moveScore(self, move, game_state, plr_id):
        gs_copy = copy.deepcopy(game_state)
        gs_copy.ExecuteMove(plr_id, move)

        # Get my move and opponent's score
        my_score = gs_copy.players[plr_id].ScoreRound()[0]
        opponent_score = gs_copy.players[int(not plr_id)].ScoreRound()[0]
        # See if that brings to the end of game
        endOfGame = self.isEndOfGame(gs_copy)
        # End of game = add bonus score for both players
        if endOfGame:
            my_score += gs_copy.players[plr_id].EndOfGameScore()
            opponent_score += gs_copy.players[int(not self.id)].EndOfGameScore()

        return (my_score - opponent_score, my_score)

    def getTopMoves(self, top_diff, top_score, results):
        # Select 10 top moves
        upper_bound = UPPER_BOUND
        upper_moves = results[:upper_bound]
        # Select moves equivalent to the top score
        top_score_moves = list(filter(lambda r: r[1] == (top_diff, top_score), results))

        # If we have more than 10 moves equivalent to the top score, return them
        if len(upper_moves) <= len(top_score_moves):
            return [move[0] for move in top_score_moves]
        # Otherwise, return the 10 top moves
        return [move[0] for move in upper_moves]


    # The minimax body
    def miniMax(self, game_state, depth, alpha, beta, isMaximizingPlayer, start_time):

        # Leaf node - return static evaluation
        if depth == 0 or not game_state.TilesRemaining():
            my_score = game_state.players[self.id].ScoreRound()[0]
            opponent_score = game_state.players[int(not self.id)].ScoreRound()[0]

            endOfGame = self.isEndOfGame(game_state)
            # End of game = add bonus score for both players
            if endOfGame:
                my_score += game_state.players[self.id].EndOfGameScore()
                opponent_score += game_state.players[int(not self.id)].EndOfGameScore()

            return (my_score - opponent_score, my_score)

        # My turn - Obtain the max evaluation value
        if isMaximizingPlayer:
            maxEvaluation = (float("-inf"), float("-inf"))
            # Obtain the available moves from the state
            avail_moves = game_state.players[self.id].GetAvailableMoves(game_state)
            # Get the moves sorted with descending score
            results = self.sortMoves(avail_moves, game_state, self.id)
            # Select the greatest difference and associated top score
            top_diff, top_score = results[0][1]
            # Only extracts moves
            new_results = self.getTopMoves(top_diff, top_score, results)

            # Evaluate the selected moves
            for avail_move in new_results:
                new_game_state = copy.deepcopy(game_state)
                new_game_state.ExecuteMove(self.id, avail_move)
                evaluation = self.miniMax(new_game_state, depth - 1, alpha, beta, False, start_time)
                maxEvaluation = max(maxEvaluation, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break

                elapsed = time.time() - start_time
                # Gonna time out! Return the current max move
                if elapsed >= TIME_THRESHOLD:
                    break

            return maxEvaluation

        # Rival's turn - Obtain the min evaluation value
        else:
            minEvaluation = (float("inf"), float("inf"))
            # Obtain the available moves from the state
            avail_moves = game_state.players[int(not self.id)].GetAvailableMoves(game_state)
            # Select the greatest difference and associated top score
            results = self.sortMoves(avail_moves, game_state, int(not self.id))
            # Select the greatest difference and associated top score
            top_diff, top_score = results[0][1]
            # Only extracts moves
            new_results = self.getTopMoves(top_diff, top_score, results)

            # Evaluate the selected moves
            for avail_move in new_results:
                new_game_state = copy.deepcopy(game_state)
                new_game_state.ExecuteMove(int(not self.id), avail_move)
                evaluation = self.miniMax(new_game_state, depth - 1, alpha, beta, True, start_time)
                minEvaluation = min(minEvaluation, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break

                elapsed = time.time() - start_time
                # Gonna time out! Return the current max move.
                if elapsed >= TIME_THRESHOLD:
                    break
            return minEvaluation


    def SelectMove(self,moves,game_state):

        # Timer
        start_time = time.time()

        # Get rid of moves which directly grab tiles to the floor line
        candidates = list(filter(lambda m: m[2].pattern_line_dest != -1, moves))
        if len(candidates) == 0:
            # Use the unfavourable moves
            candidates = moves

        # Get ranked results
        results = self.sortMoves(candidates, game_state, self.id)

        # Select the top diff - score pair
        top_diff, top_score = results[0][1]

        # New_results are moves with top score, or maximum UPPER_BOUND sub-optimal moves.
        new_results = self.getTopMoves(top_diff, top_score, results)


        maxEvaluation = (float("-inf"), float("-inf"))
        alpha = (float("-inf"), float("-inf"))
        beta = (float("inf"), float("inf"))

        # Dynamic search depth based on the branching factor
        if len(new_results) >= UPPER_BOUND:
            depth = 3
        else:
            depth = 4

        max_move = None

        # Execute minimax
        for move in new_results:
            new_game_state = copy.deepcopy(game_state)
            new_game_state.ExecuteMove(self.id, move)
            evaluation = self.miniMax(new_game_state, depth - 1, alpha, beta, False, start_time)
            if evaluation > maxEvaluation:
                maxEvaluation = evaluation
                max_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break

            elapsed = time.time() - start_time

            # Gonna time out! Return the current max move.
            if elapsed >= TIME_THRESHOLD:
                break

        return max_move


