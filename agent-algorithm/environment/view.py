from tkinter import Canvas, font, LEFT, BOTH, TRUE
from environment.settings import CANVAS_WIDTH, CANVAS_HEIGHT, GRID_SIZE, MAXROW, MAXCOL

LEFT_OFFSET = GRID_SIZE * 6
TOP_OFFSET = GRID_SIZE * 3

class TileView():
    def __init__(self, canvas, x, y, colour):
        tile_y = TOP_OFFSET + GRID_SIZE * y
        tile_x = LEFT_OFFSET + GRID_SIZE * x
        self.__rect = canvas.create_rectangle(tile_x, tile_y,
                                              tile_x + GRID_SIZE, tile_y + GRID_SIZE,
                                              fill=colour)

    def erase(self, canvas):
        canvas.delete(self.__rect)

class BlockView():
    def __init__(self, block):
        self.__block = block
        self.__tiles = []

    @property
    def block(self):
        return self.__block

    def draw(self, canvas):
        if self.__block.is_falling():
            (block_x, block_y) = self.__block.position
        else:
            block_x = -5
            block_y = 5
        bitmap = self.__block.bitmap
        self.__tiles = []
        _y = block_y
        for row in bitmap.rows:
            _x = block_x
            for tile in row:
                if tile == 1:
                    tileview = TileView(canvas, _x, _y, self.__block.colour)
                    self.__tiles.append(tileview)
                _x = _x + 1
            _y = _y + 1

    def redraw(self, canvas):
        self.erase(canvas)
        self.draw(canvas)

    def erase(self, canvas):
        for tile in self.__tiles:
            tile.erase(canvas)
        self.__tiles.clear()

class BlockfieldView():
    def __init__(self):
        self.__tiles = []

    def redraw(self, canvas, blockfield):
        for tileview in self.__tiles:
            tileview.erase(canvas)
        self.__tiles.clear()
        bitmap = blockfield.bitmap
        _y = 0
        for row in bitmap:
            _x = 0
            for tile in row:
                if tile != 0:
                    tileview = TileView(canvas, _x, _y, tile)
                    self.__tiles.append(tileview)
                _x = _x + 1
            _y = _y + 1

class View():
    def __init__(self, root, controller):
        self.__controller = controller
        root.wm_title("Bomber")
        self.__windowsystem = root.call('tk', 'windowingsystem')
        self.__frame = root
        self.__canvas = Canvas(self.__frame, width=int(CANVAS_WIDTH),
                               height=int(CANVAS_HEIGHT), bg="white")
        self.__canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.__init_fonts()
        self.__init_arena()
        self.__init_score()
        self.__block_views = []
        self.__blockfield_view = BlockfieldView()
        self.__messages = []

    def __init_fonts(self):
        self.bigfont = font.nametofont("TkDefaultFont")
        self.bigfont.configure(size=int(48))
        self.scorefont = font.nametofont("TkDefaultFont")
        self.scorefont.configure(size=int(20))


    def __init_score(self):
        self.score_text = self.__canvas.create_text(5, 5, anchor="nw")
        self.__canvas.itemconfig(self.score_text, text="Score:", font=self.scorefont)

    def __init_arena(self):
        self.__canvas.create_rectangle(LEFT_OFFSET, TOP_OFFSET,
                                       LEFT_OFFSET + MAXCOL*GRID_SIZE,
                                       TOP_OFFSET+MAXROW*GRID_SIZE, fill="black")

        nextblocktext = self.__canvas.create_text(GRID_SIZE,
                                                  TOP_OFFSET + GRID_SIZE * 4, anchor="nw")
        self.__canvas.itemconfigure(nextblocktext, text="Next:",
                                    font=self.bigfont, fill="black")

        self.__autoplay_text = self.__canvas.create_text(LEFT_OFFSET + GRID_SIZE * 5,
                                                         TOP_OFFSET - GRID_SIZE, anchor="c")
        self.__canvas.itemconfigure(self.__autoplay_text, text="Play mode",
                                    font=self.bigfont, fill="black")

    def register_block(self, block):
        block_view = BlockView(block)
        self.__block_views.append(block_view)

    def unregister_block(self, block):
        for block_view in self.__block_views:
            if block_view.block is block:
                block_view.erase(self.__canvas)
                self.__block_views.remove(block_view)

    def update_blockfield(self, blockfield):
        self.__blockfield_view.redraw(self.__canvas, blockfield)

    def display_score(self):
        self.__canvas.itemconfig(self.score_text, text="Score: " + str(self.__controller.score),
                                 font=self.scorefont)

    def show_autoplay(self, autoplay):
        if autoplay:
            self.__canvas.itemconfig(self.__autoplay_text, text="Auto-play mode",
                                     font=self.scorefont, fill="black")
        else:
            self.__canvas.itemconfig(self.__autoplay_text, text="Manual mode",
                                     font=self.scorefont, fill="black")

    def game_over(self):
        text1 = self.__canvas.create_text(LEFT_OFFSET + GRID_SIZE*MAXCOL//2,
                                          CANVAS_HEIGHT/2, anchor="c")
        text2 = self.__canvas.create_text(LEFT_OFFSET + GRID_SIZE*MAXCOL//2,
                                          CANVAS_HEIGHT/2 + 100, anchor="c")
        text1_shadow = self.__canvas.create_text(2 + LEFT_OFFSET + GRID_SIZE*MAXCOL//2,
                                                 2 + CANVAS_HEIGHT/2, anchor="c")
        text2_shadow = self.__canvas.create_text(2 + LEFT_OFFSET + GRID_SIZE*MAXCOL//2,
                                                 2 + CANVAS_HEIGHT/2 + 100, anchor="c")
        self.__messages.append(text1)
        self.__messages.append(text2)
        self.__messages.append(text1_shadow)
        self.__messages.append(text2_shadow)
        self.__canvas.itemconfig(text1, text="GAME OVER!",
                                 font=self.bigfont, fill="white")
        self.__canvas.itemconfig(text2, text="Press r to play again.",
                                 font=self.scorefont, fill="white")
        self.__canvas.itemconfig(text1_shadow, text="GAME OVER!",
                                 font=self.bigfont, fill="black")
        self.__canvas.itemconfig(text2_shadow, text="Press r to play again.",
                                 font=self.scorefont, fill="black")
        self.__canvas.tag_raise(text1)
        self.__canvas.tag_raise(text2)

    def clear_messages(self):
        for txt in self.__messages:
            self.__canvas.delete(txt)
        self.__messages.clear()

    def update(self):
        for block_view in self.__block_views:
            block_view.redraw(self.__canvas)
        self.display_score()
