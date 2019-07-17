from pathlib import Path
import pickle
import operator
from collections import OrderedDict

class TriviaHighScoreTable():
    """description of class"""

    def __init__(self, *args, **kwargs):
        self.players = {}
        self.highest_score = 0
        self.file = Path('./trivia_highscores.dat')

    def writeToFile(self):
        pickle.dump(self.players,self.file.open('wb'))

    def readFromFile(self):
        self.players = pickle.load(self.file.open('rb'))
        self.players = OrderedDict(sorted(self.players.items(), key=lambda kv: kv[1]))

        self.highest_score = max(self.players.values(), key=self.players.get)

    def addUserScore(self,pid,score):
        if pid in self.players:
            self.players[pid] += score
        else:
            self.players[pid] = score
       
