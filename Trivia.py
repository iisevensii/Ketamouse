from pathlib import Path
from TriviaQuestion import TriviaQuestion
from TriviaHighScoreTable import TriviaHighScoreTable
from random import choice

class Trivia():
    """description of class"""
    def __init__(self, *args, **kwargs):
        self.current_subject = args[0]
        self.question_files = [x for x in Path('./trivia_questions/').iterdir() if x.is_file()]
        self.highscores = TriviaHighScoreTable()
        self.started = False
        self.initialized = True
        self.host = 0
        self.max_score = args[1]

        self.time_since_asked = None

        self.current_question = None
        self.current_questions = []
        self.current_players = {} #player id, score
        self.answers_given = []      

        for path in self.question_files:
            if path.stem.lower() == str(args[0]).lower():
                data = path.read_text().split("\n")

                for entry in data:
                    if len(entry) == 0:
                        continue
                    question = entry.split('|')
                    addend = TriviaQuestion(question[0],tuple(question[1].split(",")),tuple(question[2].split(",")))
                    addend.category = path.stem
                    self.current_questions.append(addend)
                    self.getNextQuestion()
                break
        else:
            self.current_questions = []
            self.initialized = False

    def addPlayer(self,pid):
        self.current_players[pid] = 0

    def getNextQuestion(self):
        self.answers_given.clear()
        self.current_question = choice(self.current_questions)
        return self.current_question

    def giveAnswer(self,ans):
        self.answers_given.append(ans.lower())
        return self.current_question.getAnswerPoints(ans)

    def givePoints(self, pid, pval):
        self.current_players[pid] += pval
        self.highscores.addUserScore(pid,pval)

    def End(self):
        self.highscores.writeToFile()
        self.initialized = False
        self.host = 0
        self.started = False

        #return max(self.current_players, key=self.current_players.get)









