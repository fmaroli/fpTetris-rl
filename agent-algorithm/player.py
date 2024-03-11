from environment.settings import Direction, MAXROW, MAXCOL

class Player():
    def __init__(self, controller):
        self.controller = controller

    def prox_move(self, gamestate):
        posMoves = []
        points = []

        for mv in range(-2, 8):
            for rot in range(0, 3):
                clone = gamestate.clone(True)
                landed = False
                while not landed:
                    self.move(clone, mv, rot)
                    landed = clone.update()
                posMoves.append((mv, rot))
                self.calPoints(clone, points, rot)
            bestMove = (self.bestMove(points, posMoves))
        self.move(gamestate, bestMove[0], bestMove[1])

    def move(self, gamestate, target_pos, target_rot):
        x, y = gamestate.get_falling_block_position()
        dir = None
        if target_pos < x:
            dir = Direction.LEFT
        elif target_pos > x:
            dir = Direction.RIGHT
        if dir != None:
            gamestate.move(dir)
        ang = gamestate.get_falling_block_angle()
        dir = None
        if target_rot == 3 and ang == 0:
            dir = Direction.LEFT
        elif target_rot > ang:
            dir = Direction.RIGHT
        if dir != None:
            gamestate.rotate(dir)

    def getHeight(self, gamestate, COL):
        tiles = gamestate.get_tiles()
        height = 0
        for line in range(0, MAXROW):
            if tiles[line][COL] != 0:
                if (20 - line) > height:
                    height = 20 - line
                return height

    def noneToInt(self, result):
        return int(0 if result is None else result)

    def changeInHeight(self, gamestate):
        listHeights = []
        heightVar = 0
        for COL in range(0, MAXCOL):
            listHeights.append(self.noneToInt(self.getHeight(gamestate, COL)))
        for pairs in range(0, MAXCOL - 1):
            heightVar = heightVar + abs(listHeights[pairs] - listHeights[pairs + 1])
        return heightVar

    def setHole(self, gamestate):
        tiles = gamestate.get_tiles()
        holes = 0
        listHeights = []
        for COL in range(0, MAXCOL):
            listHeights.append(self.noneToInt(self.getHeight(gamestate, COL)))
        for COL in range(0, MAXCOL):
            for ROW in range(20 - listHeights[COL], MAXROW):
                if COL != 0 | COL != MAXCOL:
                    if (tiles[ROW][COL] == 0) & ((tiles[ROW - 1][COL + 1] != 0) | (tiles[ROW - 1][COL - 1] != 0)):
                        holes += 1
                else:
                    if (tiles[ROW][COL] == 0):
                        holes += 1
        return holes

    def setBarricade(self, gamestate):
        tiles = gamestate.get_tiles()
        blocks = 0
        holY = 0
        listHeights = []
        for COL in range(0, MAXCOL):
            listHeights.append(self.noneToInt(self.getHeight(gamestate, COL)))
        for COL in range(0, MAXCOL):
            holY = 0
            for ROW in range(20 - listHeights[COL], 20):
                if tiles[ROW][COL] == 0:
                    previousLine = 0
                    if ROW > previousLine:
                        holY = ROW
                        for holeRange in range(20 - listHeights[COL], holY):
                            if tiles[holeRange][COL] != 0:
                                blocks += 1
        return blocks

    def calPoints(self, gamestate, pointList, rotation):
        """totalHeightPoints = self.totalHeights(gamestate)"""
        totalVarPoints = self.changeInHeight(gamestate)
        countHoles = self.setHole(gamestate)
        """totalPoints = gamestate.get_Points()"""
        countBlocks = self.setBarricade(gamestate)
        touchPoints = self.touchSide(gamestate)
        """blockBonus = self.blockTypeBonus(gamestate)"""
        totalPoints = - 3 * countHoles - 1.5 * totalVarPoints - countBlocks + 0.05 * touchPoints
        """- 0.51 * totalHeightPoints - 0.18 * totalVariationPoints + 0.7 * totalPoints - 0.35 * totalHole - 0.2 * totalBlocks + 0.1 * blockBonus"""
        pointList.append(totalPoints)

    def touchSide(self, gamestate):
        tiles = gamestate.get_tiles()
        touchPoints = 0
        for ROW in range(0, 19):
            if (tiles[ROW][0] != 0) | (tiles[ROW][9] != 0):
                touchPoints += 12
            elif (tiles [ROW][1] != 0) | (tiles [ROW][8] != 0):
                touchPoints += 8
            elif (tiles [ROW][2] != 0) | (tiles [ROW][7] != 0):
                touchPoints += 6
            elif (tiles [ROW][3] != 0) | (tiles [ROW][6] != 0):
                touchPoints += 4
            elif (tiles [ROW][4] != 0) | (tiles [ROW][5] != 0):
                touchPoints += 2
        return touchPoints

    def bestMove(self, pointList, posMoves):
        maxPoints = max(pointList)
        for i in range(0, len(pointList)):
            if pointList[i] == maxPoints:
                temp = i
                calcMove = posMoves[temp]
                posMoves = []
                pointList = []
                return calcMove