from environment.settings import MAXROW, MAXCOL

class GameState():
    def __init__(self, model):
        self.__model = model
        self.__is_a_clone = False

    def get_falling_block_position(self):
        return self.__model.falling_block_position

    def get_falling_block_angle(self):
        return self.__model.falling_block_angle

    def get_falling_block_tiles(self):
        tilescopy = self.__model.get_falling_block_tiles()
        return tilescopy

    def get_next_block_tiles(self):
        tilescopy = self.__model.get_next_block_tiles()
        return tilescopy

    def get_falling_block_type(self):
        return self.__model.falling_block_type

    def get_next_block_type(self):
        return self.__model.next_block_type

    def print_block_tiles(self):
        tiles = self.get_falling_block_tiles()
        txt = ""
        size = len(tiles)
        for _y in range(0, size):
            for _x in range(0, size):
                if tiles[_y][_x] != 0:
                    txt += '#'
                else:
                    txt += '.'
            txt += '\n'
        print(txt)

    def get_tiles(self):
        tilescopy = self.__model.get_copy_of_tiles()
        return tilescopy

    def print_tiles(self):
        tiles = self.get_tiles()
        txt = ""
        for _y in range(0, MAXROW):
            for _x in range(0, MAXCOL):
                if tiles[_y][_x] != 0:
                    txt += '#'
                else:
                    txt += '.'
            txt += '\n'
        print(txt)

    def get_score(self):
        return self.__model.score

    def clone(self, is_dummy):
        game = GameState(self.__model)
        game._set_model(self.__model.clone(is_dummy), True)
        return game

    def _set_model(self, model, is_a_clone):
        self.__model = model
        self.__is_a_clone = is_a_clone

    def move(self, direction):
        self.__model.move(direction)


    def rotate(self, direction):
        self.__model.rotate(direction)

    def update(self):
        if self.__model.is_dummy:
            (_, landed) = self.__model.update()
            return landed
        return False
