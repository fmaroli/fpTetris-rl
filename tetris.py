from environment.controller import Controller
from player import Player

class Game():
    def __init__(self):
        self.controller = Controller()
        self.player = Player(self.controller)

    def run(self):
        self.controller.run(self.player)

Game().run()
