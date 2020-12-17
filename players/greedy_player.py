from advance_model import *
from utils import *

import time
import random

class myPlayer(AdvancePlayer):
    def __init__(self,_id):
        super().__init__(_id)

    def SelectMove(self,moves,game_state):

        # Filter out moves which directly grab tiles to the floor line
        candidates = list(filter(lambda m: m[2].pattern_line_dest != -1, moves))
        result = []
        
        # Use the original move list if all candidates are filtered out
        if len(candidates) == 0:
            candidates = moves
        
        # Get the estimate excpetation of the candidate move list
        result = self.getGreedy(candidates, game_state, self.id)

        # Filter out best 5 (including tie) candidates, or all No.1 ranked options
        # Variable result is reused to refer to No.1 ranked options
        # Variable candidates is reused to refer to non - No.1 ranked options
        # Also, stop looping for more candidates if the score is way lower than the top result
            
        top_score = result[0][1]
        if len(result) > 5:
            candidates = result
            result = []
            while True:
                best_score = candidates[0][1]
                #THRESHOLD = 2
                if best_score < top_score - 2:
                    break
                result = result + list(filter(lambda r: r[1] == best_score, candidates))
                if len(result) >= 5:
                    break
                else:
                    candidates = list(filter(lambda r: r[1] != best_score, candidates))

        # Variable candidates is reused to store temporary result
        # To calculate the rank after considering the impact on the opponent's performance
        candidates = []
        for decision in result:
            candidates.append(self.thinkFurther(decision))

        # Get result sorted and return the top choice
        result = sorted(candidates, key = lambda x: (x[1], x[2]), reverse = True)
        return result[0][0]

    # Get the estimate excpetation of a move list
    def getGreedy(self, candidates, game_state, id):
        result = []

        for move in candidates:
            score, new_state = self.moveScore(move, game_state, id)
            result.append((move, score, new_state))

        return sorted(result, key = lambda x: x[1], reverse = True)

    # Get the estimate excpetation after executing the move
    def moveScore(self, move, game_state, id):
        gs_copy = copy.deepcopy(game_state)
        gs_copy.ExecuteMove(id, move)
        return (gs_copy.players[id].ScoreRound()[0], gs_copy)

    # Calculate the impact on the available moves of the opponent    
    def thinkFurther(self, decision):
        # Get the opponent's ID
        oppo_id  = None
        if self.id == 1:
            oppo_id = 0
        else:
            oppo_id = 1
        move, score, new_state = decision
        
        # Get opponent's available move
        oppo_moves = new_state.players[oppo_id].GetAvailableMoves(new_state)
        oppo_result = self.getGreedy(oppo_moves, new_state, oppo_id)
        top = 0
        avg = 0
        
        # Calculate the top score and the average score
        if len(oppo_result) != 0:
            top = oppo_result[0][1]
            avg = sum(map(lambda x: x[1], oppo_result)) / len(oppo_result)
            
        # Return move, difference between score & oppo's top score, negative oppo's average score
        # Oppo's average score is negative for the purpose of ranking
        return (move, score - top, 0 - avg)
