from random import Random
from tkinter import Tk
from environment.settings import Direction, MAXCOL, MAXROW, DEFAULT_AUTOPLAY, DISABLE_DISPLAY
from environment.model import Model
from environment.gamestate import GameState
from environment.view import View
from player import Player

class Controller():
    def __init__(self):
        if not DISABLE_DISPLAY:
            self.__root = Tk()
            self.__windowsystem = self.__root.call('tk', 'windowingsystem')
            self.__root.bind_all('<Key>', self.key)
        self.__running = True
        self.__score = -1
        self.__autoplay = not DEFAULT_AUTOPLAY
        self.__gen_random()
        self.__model = Model(self)
        self.__gamestate_api = GameState(self.__model)
        if not DISABLE_DISPLAY:
            self.__view = View(self.__root, self)
        self.__blockfield = self.__model.blockfield
        self.__lost = False
        self.__model.start()
        self.__model.enable_autoplay(self.__autoplay)

    def __gen_random(self):
        self.__rand = Random()
        self.rand_ix = 0
        self.maxrand = 100000
        maxblocktype = 6
        self.randlist = []
        for _i in range(self.maxrand):
            self.randlist.append(self.__rand.randint(0, maxblocktype))

    def get_random_blocknum(self):
        self.rand_ix = (self.rand_ix + 1) % self.maxrand
        return self.randlist[self.rand_ix]

    def register_block(self, block):
        if not DISABLE_DISPLAY:
            self.__view.register_block(block)

    def unregister_block(self, block):
        if not DISABLE_DISPLAY:
            self.__view.unregister_block(block)

    def update_blockfield(self, blockfield):
        self.__blockfield = blockfield
        if not DISABLE_DISPLAY:
            self.__view.update_blockfield(blockfield)

    def update_score(self, score):
        self.__score = score

    @property
    def score(self):
        return self.__score

    def game_over(self):
        self.__lost = True
        if DISABLE_DISPLAY:
            print("Score: ", self.__score)
            self.__running = False
        else:
            self.__view.game_over()

    def key(self, event):
        if event.char == ' ':
            self.__model.drop_block()
        elif event.char == 'q':
            self.__running = False
        elif event.char == 'a':
            self.__model.move(Direction.LEFT)
        elif event.char == 's':
            self.__model.move(Direction.RIGHT)
        elif event.char == 'k':
            self.__model.rotate(Direction.LEFT)
        elif event.char == 'l':
            self.__model.rotate(Direction.RIGHT)
        elif event.char == 'y':
            self.__autoplay = not self.__autoplay
            self.__model.enable_autoplay(self.__autoplay)
            if not DISABLE_DISPLAY:
                self.__view.show_autoplay(self.__autoplay)
        elif event.char == 'r':
            if not DISABLE_DISPLAY:
                self.__view.clear_messages()
            self.__lost = False
            self.__model.restart()
            self.__model.enable_autoplay(self.__autoplay)

    def run(self, player):
        dropped = False
        while self.__running:
            if not self.__lost:
                if dropped and self.__autoplay:
                    self.__model.reset_counts()
                    player.prox_move(self.__gamestate_api)
                (dropped, _landed) = self.__model.update()
            if not DISABLE_DISPLAY:
                self.__view.update()
                self.__root.update()
        if not DISABLE_DISPLAY:
            self.__root.destroy()
