from pathlib import Path
class TriviaQuestion():
    """description of class"""
    
    def __init__(self, *args, **kwargs):
        self.question = args[0]
        self.best_answers = args[1]
        self.moderate_answers = args[2]
        self.category = ''

    def getAnswerPoints(self, ans : str):
        if ans.lower() in [x.lower() for x in self.best_answers]:
            return 100
        elif ans.lower() in [x.lower() for x in self.moderate_answers]:
            return 50
        else:
            return 0


            
            
