from copy import deepcopy, copy
import time
from environment.settings import MAXROW, MAXCOL, Direction

class BlockBitmap():
    def __init__(self, rows, colour):
        self.rows = rows
        self.colour = colour
        self.size = len(rows)
        self.calculate_bounding_box()

    def str(self):
        txt = ""
        for row in self.rows:
            for tile in row:
                if tile == 0:
                    txt = txt + '.'
                else:
                    txt = txt + '#'
            txt = txt + '\n'
        return txt

    def clone(self):
        rows = []
        for row in self.rows:
            newrow = []
            for tile in row:
                newrow.append(tile)
            rows.append(newrow)
        return BlockBitmap(rows, self.colour)

    def get_copy_of_tiles(self):
        newrows = []
        for row in self.rows:
            newrows.append(tuple(row))
        return newrows

    def calculate_bounding_box(self):
        x_min = 4
        x_max = 0
        y_min = 4
        y_max = 0
        for _y in range(0, self.size):
            for _x in range(0, self.size):
                if self.rows[_y][_x] == 1:
                    if _x < x_min:
                        x_min = _x
                    if _y < y_min:
                        y_min = _y
                    if _x > x_max:
                        x_max = _x
                    if _y > y_max:
                        y_max = _y
        self.bounding_box = (x_min, y_min, x_max, y_max)

    def rotate(self, direction):
        if self.size == 3:
            newrows = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        else:
            newrows = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        if direction == Direction.RIGHT:
            _x = self.size - 1
            for row in self.rows:
                _y = 0
                for tile in row:
                    newrows[_y][_x] = tile
                    _y = _y + 1
                _x = _x - 1
        else:
            _x = 0
            for row in self.rows:
                _y = self.size - 1
                for tile in row:
                    newrows[_y][_x] = tile
                    _y = _y - 1
                _x = _x + 1
        self.rows = newrows
        self.calculate_bounding_box()

class IBlock(BlockBitmap):
    def __init__(self):
        BlockBitmap.__init__(self, ((0,0,0,0), (1,1,1,1), (0,0,0,0), (0,0,0,0)), "cyan")

class JBlock(BlockBitmap):
    def __init__(self):
        BlockBitmap.__init__(self, ((1,0,0), (1,1,1), (0,0,0)), "blue")

class LBlock(BlockBitmap):
    def __init__(self):
        BlockBitmap.__init__(self, ((0,0,1), (1,1,1), (0,0,0)), "orange")

class OBlock(BlockBitmap):
    def __init__(self):
        BlockBitmap.__init__(self, ((0,0,0,0), (0,1,1,0), (0,1,1,0), (0,0,0,0)), "yellow")

class SBlock(BlockBitmap):
    def __init__(self):
        BlockBitmap.__init__(self, ((0,1,1), (1,1,0), (0,0,0)), "green")

class TBlock(BlockBitmap):
    def __init__(self):
        BlockBitmap.__init__(self, ((0,1,0), (1,1,1), (0,0,0)), "purple")

class ZBlock(BlockBitmap):
    def __init__(self):
        BlockBitmap.__init__(self, ((1,1,0), (0,1,1), (0,0,0)), "red")


class Block():
    def __init__(self, block_type, x, y, falling):
        self.__x = x
        self.__y = y
        self.__angle = 0
        self.__type = block_type
        self.__falling = falling
        if block_type == 'I':
            self.__bitmap = IBlock()
        elif block_type == 'J':
            self.__bitmap = JBlock()
        elif block_type == 'L':
            self.__bitmap = LBlock()
        elif block_type == 'O':
            self.__bitmap = OBlock()
        elif block_type == 'S':
            self.__bitmap = SBlock()
        elif block_type == 'T':
            self.__bitmap = TBlock()
        elif block_type == 'Z':
            self.__bitmap = ZBlock()

    @property
    def position(self):
        return (self.__x, self.__y)

    @property
    def angle(self):
        return self.__angle

    @property
    def bitmap(self):
        return self.__bitmap

    @property
    def colour(self):
        return self.__bitmap.colour

    @property
    def type(self):
        return self.__type

    @property
    def bounding_box(self):
        return self.__bitmap.bounding_box

    def is_falling(self):
        return self.__falling

    def fall(self):
        self.__falling = True

    def move(self, blockfield, direction):
        _x = self.__x + direction.value
        (xmin, _, xmax, _) = self.bounding_box
        if _x + xmin < 0 or _x + xmax >= MAXCOL:
            return False
        if blockfield.collision(self, direction.value, 0):
            return False
        self.__x = _x
        return True

    def rotate(self, blockfield, direction):
        oldbitmap = self.__bitmap
        newbitmap = self.__bitmap.clone()
        orig_angle = self.__angle
        orig_x = self.__x
        orig_y = self.__y
        self.__angle = self.__angle + direction.value
        if self.__angle < 0:
            self.__angle = self.__angle + 4
        elif self.__angle > 3:
            self.__angle = self.__angle - 4
        newbitmap.rotate(direction)
        self.__bitmap = newbitmap
        (xmin, _, xmax, _) = self.bounding_box
        while self.__x + xmin < 0:
            self.__x = self.__x + 1
        while self.__x + xmax >= MAXCOL:
            self.__x = self.__x - 1
        if blockfield.collision(self, 0, 0):
            self.__bitmap = oldbitmap
            self.__x = orig_x
            self.__y = orig_y
            self.__angle = orig_angle

    def drop(self, blockfield):
        (_, block_y) = self.position
        (_, _, _, ymax) = self.bounding_box
        if (block_y + ymax == MAXROW-1) or blockfield.collision(self, 0, 1):
            score = blockfield.land(self)
            return (True, score)
        self.__y = self.__y + 1
        return (False, 0)

    def get_copy_of_tiles(self):
        return self.__bitmap.get_copy_of_tiles()

class BlockField():
    def __init__(self):
        self.__tiles = []
        for _y in range(0, MAXROW):
            tilerow = []
            for _x in range(0, MAXCOL):
                tilerow.append(0)
            self.__tiles.append(tilerow)

    @property
    def bitmap(self):
        return self.__tiles

    def get_copy_of_tiles(self):
        newtiles = []
        for row in self.__tiles:
            newtiles.append(tuple(row))
        return newtiles

    def collision(self, block, xoffset, yoffset):
        (block_x, block_y) = block.position
        (xmin, ymin, xmax, ymax) = block.bounding_box

        if ymax + block_y + yoffset >= MAXROW:
            return True
        if xmax + block_x + xoffset >= MAXCOL:
            return True

        bitmap = block.bitmap.rows
        for _y in range(ymin, ymax+1):
            for _x in range(xmin, xmax+1):
                if bitmap[_y][_x] != 0:
                    if self.__tiles[block_y + _y + yoffset][block_x + _x + xoffset] != 0:
                        return True
        return False

    def land(self, block):
        (block_x, block_y) = block.position
        bitmap = block.bitmap.rows
        (xmin, ymin, xmax, ymax) = block.bounding_box
        for _y in range(ymin, ymax+1):
            for _x in range(xmin, xmax+1):
                if bitmap[_y][_x] != 0:
                    self.__tiles[block_y + _y][block_x + _x] = block.colour
        score = self.check_full_rows()
        return score

    def drop_row(self, row_to_drop):
        for _y in range(row_to_drop, 0, -1):
            self.__tiles[_y] = self.__tiles[_y - 1]
        blankrow = []
        for _x in range(0, MAXCOL):
            blankrow.append(0)
        self.__tiles[0] = blankrow

    def check_full_rows(self):
        scores = [0, 100, 400, 800, 1600]
        rows_dropped = 0
        for _y in range(0, MAXROW):
            count = 0
            for _x in range(0, MAXCOL):
                if self.__tiles[_y][_x] != 0:
                    count = count+1
            if count == MAXCOL:
                self.drop_row(_y)
                rows_dropped = rows_dropped + 1
        return scores[rows_dropped]

class Model():
    def __init__(self, controller):
        self.__controller = controller
        self.blocktypes = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
        self.__falling_block = 0
        self.__is_dummy = False
        self.__blockfield = None
        self.__next_block = None
        self.__score = 0
        self.__last_drop = 0
        self.__moves = 0
        self.__rotates = 0
        self.__autoplay = False
        self.__move_time = 0.5

    def start(self):
        self.restart()

    def clone(self, is_dummy):
        newmodel = copy(self)
        newmodel.copy_in_state(is_dummy, deepcopy(self.__blockfield),
                               deepcopy(self.__falling_block),
                               deepcopy(self.__next_block))
        return newmodel

    def copy_in_state(self, is_dummy, blockfield, falling_block, next_block):
        self.__is_dummy = is_dummy
        self.__blockfield = blockfield
        self.__falling_block = falling_block
        self.__next_block = next_block


    @property
    def blockfield(self):
        return self.__blockfield

    @property
    def falling_block_position(self):
        return self.__falling_block.position

    @property
    def falling_block_angle(self):
        return self.__falling_block.angle

    @property
    def falling_block_type(self):
        return self.__falling_block.type

    @property
    def next_block_type(self):
        return self.__next_block.type

    def get_falling_block_tiles(self):
        return self.__falling_block.get_copy_of_tiles()

    def get_next_block_tiles(self):
        return self.__next_block.get_copy_of_tiles()

    def get_copy_of_tiles(self):
        return self.__blockfield.get_copy_of_tiles()

    def init_score(self):
        self.__score = 0
        if not self.__is_dummy:
            self.__controller.update_score(0)

    @property
    def score(self):
        return self.__score

    @property
    def is_dummy(self):
        return self.__is_dummy

    def __create_new_block(self, falling):
        block_x = MAXCOL//2 - 2
        block_y = 0
        blocknum = self.__controller.get_random_blocknum()
        blocktype = self.blocktypes[blocknum]
        block = Block(blocktype, block_x, block_y, falling)
        return block

    def __check_falling_block(self, now):
        if (now - self.__last_drop > self.__move_time) or self.__is_dummy:
            self.__score = self.__score + 1
            (landed, scorechange) = self.__falling_block.drop(self.__blockfield)
            self.__last_drop = now
            if landed:
                (_, block_y) = self.__falling_block.position
                if block_y == 0:
                    self.__game_over()
                else:
                    self.__score = self.__score + scorechange
                    self.__start_next_block()
            return True, landed
        return False, False

    def __start_next_block(self):
        if not self.__is_dummy:
            self.__controller.unregister_block(self.__falling_block)
        self.__falling_block = self.__next_block
        self.__falling_block.fall()
        self.__next_block = self.__create_new_block(False)
        if not self.__is_dummy:
            self.__controller.register_block(self.__next_block)
            self.__controller.update_blockfield(self.__blockfield)
            self.__controller.update_score(self.__score)

    def move(self, direction):
        self.__moves += 1
        if self.__moves > 1 and self.__autoplay:
            print("Illegal move - can't move twice per update")
            return False
        return self.__falling_block.move(self.__blockfield, direction)

    def rotate(self, direction):
        self.__rotates += 1
        if self.__rotates > 1 and self.__autoplay:
            print("Illegal rotate - can't rotate twice per update")
            return False
        return self.__falling_block.rotate(self.__blockfield, direction)

    def reset_counts(self):
        self.__moves = 0
        self.__rotates = 0

    def drop_block(self):
        landed = False
        while not landed:
            (landed, scorechange) = self.__falling_block.drop(self.__blockfield)
        (_, block_y) = self.__falling_block.position
        if block_y == 0:
            self.__game_over()
        else:
            self.__score = self.__score + scorechange
            self.__start_next_block()

    def __game_over(self):
        if not self.__is_dummy:
            self.__controller.game_over()

    def restart(self):
        self.init_score()
        if self.__falling_block != 0:
            self.__controller.unregister_block(self.__falling_block)
            self.__controller.unregister_block(self.__next_block)
        self.__next_block = self.__create_new_block(False)
        self.__falling_block = self.__create_new_block(True)
        self.__controller.register_block(self.__falling_block)
        self.__controller.register_block(self.__next_block)
        self.__last_drop = 0.0
        self.__blockfield = BlockField()
        self.__controller.update_blockfield(self.__blockfield)
        self.__autoplay = False
        self.__move_time = 0.5
        self.reset_counts()

    def enable_autoplay(self, state):
        self.__autoplay = state
        if state:
            self.__move_time = 0.01  # bot playing velocity
        else:
            self.__move_time = 0.5

    def update(self):
        now = time.time()
        self.reset_counts()
        if not self.__is_dummy:
            self.__controller.update_score(self.__score)
        (dropped, landed) = self.__check_falling_block(now)
        return (dropped, landed)
