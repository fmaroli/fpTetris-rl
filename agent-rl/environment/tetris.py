import numpy as np
from PIL import Image
import cv2
import torch
import random

class Tetris:
    piece_colors = [
        (10, 10, 10), #background
        (255, 255, 0),
        (128, 0, 128),
        (0, 255, 0),
        (255, 0, 0),
        (0, 0, 255),
        (255, 127, 0),
        (127, 127, 127)
    ]

    shapes = [
        [[1, 1], #O
         [1, 1]],

        [[0, 2, 0], #T
         [2, 2, 2]],

        [[0, 3, 3], #Z
         [3, 3, 0]],

        [[4, 4, 0], #S
         [0, 4, 4]],

        [[5, 5, 5, 5]], #I

        [[0, 0, 6], #L
         [6, 6, 6]],

        [[7, 0, 0], #J
         [7, 7, 7]]
    ]

    def __init__(self, height=20, width=10, block_m=20):
        self.height = height
        self.width = width
        self.block_m = block_m
        self.restart()

    def restart(self):
        self.board = [[0] * self.width for _ in range(self.height)]
        self.points = 0
        self.pieces = 0
        self.lines_cleared = 0
        self.bags = list(range(len(self.shapes)))
        random.shuffle(self.bags)
        self.index = self.bags.pop()
        self.piece = [row[:] for row in self.shapes[self.index]]
        self.current_pos = {"x": self.width // 2 - len(self.piece[0]) // 2, "y": 0}
        self.gameover = False
        return self.get_gamestate(self.board)

    def rot(self, piece):
        num_rows_orig = num_cols_new = len(piece)
        num_rows_new = len(piece[0])
        rotated_array = []

        for i in range(num_rows_new):
            new_row = [0] * num_cols_new
            for j in range(num_cols_new):
                new_row[j] = piece[(num_rows_orig - 1) - j][i]
            rotated_array.append(new_row)
        return rotated_array

    def get_gamestate(self, board):
        lines_cleared, board = self.is_row_clear(board)
        holes = self.get_void(board)
        bumpiness, height = self.get_height_bump(board)

        return torch.FloatTensor([lines_cleared, holes, bumpiness, height])

    def get_void(self, board):
        num_holes = 0
        for col in zip(*board):
            row = 0
            while row < self.height and col[row] == 0:
                row += 1
            num_holes += len([x for x in col[row + 1:] if x == 0])
        return num_holes

    def get_height_bump(self, board):
        board = np.array(board)
        mask = board != 0
        invert_heights = np.where(mask.any(axis=0), np.argmax(mask, axis=0), self.height)
        heights = self.height - invert_heights
        total_height = np.sum(heights)
        currs = heights[:-1]
        nexts = heights[1:]
        diffs = np.abs(currs - nexts)
        total_bumpiness = np.sum(diffs)
        return total_bumpiness, total_height

    def get_nxt_state(self):
        states = {}
        piece_id = self.index
        curr_piece = [row[:] for row in self.piece]
        if piece_id == 0:  # O piece
            num_rotations = 1
        elif piece_id == 2 or piece_id == 3 or piece_id == 4:
            num_rotations = 2
        else:
            num_rotations = 4

        for i in range(num_rotations):
            valid_xs = self.width - len(curr_piece[0])
            for x in range(valid_xs + 1):
                piece = [row[:] for row in curr_piece]
                pos = {"x": x, "y": 0}
                while not self.check_hits(piece, pos):
                    pos["y"] += 1
                self.trunc(piece, pos)
                board = self.guarda(piece, pos)
                states[(x, i)] = self.get_gamestate(board)
            curr_piece = self.rot(curr_piece)
        return states

    def get_board_state(self):
        board = [x[:] for x in self.board]
        for y in range(len(self.piece)):
            for x in range(len(self.piece[y])):
                board[y + self.current_pos["y"]][x + self.current_pos["x"]] = self.piece[y][x]
        return board

    def create_piece(self):
        if not len(self.bags):
            self.bags = list(range(len(self.shapes)))
            random.shuffle(self.bags)
        self.index = self.bags.pop()
        self.piece = [row[:] for row in self.shapes[self.index]]
        self.current_pos = {"x": self.width // 2 - len(self.piece[0]) // 2,
                            "y": 0
                            }
        if self.check_hits(self.piece, self.current_pos):
            self.gameover = True

    def check_hits(self, piece, pos):
        future_y = pos["y"] + 1
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if future_y + y > self.height - 1 or self.board[future_y + y][pos["x"] + x] and piece[y][x]:
                    return True
        return False

    def trunc(self, piece, pos):
        gameover = False
        last_collision_row = -1
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if self.board[pos["y"] + y][pos["x"] + x] and piece[y][x]:
                    if y > last_collision_row:
                        last_collision_row = y

        if pos["y"] - (len(piece) - last_collision_row) < 0 and last_collision_row > -1:
            while last_collision_row >= 0 and len(piece) > 1:
                gameover = True
                last_collision_row = -1
                del piece[0]
                for y in range(len(piece)):
                    for x in range(len(piece[y])):
                        if self.board[pos["y"] + y][pos["x"] + x] and piece[y][x] and y > last_collision_row:
                            last_collision_row = y
        return gameover

    def guarda(self, piece, pos):
        board = [x[:] for x in self.board]
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if piece[y][x] and not board[y + pos["y"]][x + pos["x"]]:
                    board[y + pos["y"]][x + pos["x"]] = piece[y][x]
        return board

    def is_row_clear(self, board):
        to_delete = []
        for i, row in enumerate(board[::-1]):
            if 0 not in row:
                to_delete.append(len(board) - 1 - i)
        if len(to_delete) > 0:
            board = self.clear_row(board, to_delete)
        return len(to_delete), board

    def clear_row(self, board, indices):
        for i in indices[::-1]:
            del board[i]
            board = [[0 for _ in range(self.width)]] + board
        return board

    def step(self, action, render=True, video=None):
        x, num_rotations = action
        self.current_pos = {"x": x, "y": 0}
        for _ in range(num_rotations):
            self.piece = self.rot(self.piece)

        while not self.check_hits(self.piece, self.current_pos):
            self.current_pos["y"] += 1
            if render:
                self.render(video)

        overflow = self.trunc(self.piece, self.current_pos)
        if overflow:
            self.gameover = True

        self.board = self.guarda(self.piece, self.current_pos)

        lines_cleared, self.board = self.is_row_clear(self.board)
        score = 1 + (lines_cleared ** 2) * self.width
        self.points += score
        self.pieces += 1
        self.lines_cleared += lines_cleared
        if not self.gameover:
            self.create_piece()
        if self.gameover:
            self.points -= 2

        return score, self.gameover

    def render(self, video=None):
        if not self.gameover:
            img = [self.piece_colors[p] for row in self.get_board_state() for p in row]
        else:
            img = [self.piece_colors[p] for row in self.board for p in row]
        img = np.array(img).reshape((self.height, self.width, 3)).astype(np.uint8)
        img = img[..., ::-1]
        img = Image.fromarray(img, "RGB")
        img = img.resize((self.width * self.block_m, self.height * self.block_m), 0)
        img = np.array(img)
        img[[i * self.block_m for i in range(self.height)], :, :] = 0
        img[:, [i * self.block_m for i in range(self.width)], :] = 0

        cv2.putText(img, "Lines cleared: "+str(self.lines_cleared),(10, 20),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(255, 255, 255))

        if video:
            video.write(img)

        cv2.imshow("DQN", img)
        cv2.waitKey(1)
