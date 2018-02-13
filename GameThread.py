import pygame
from pygame.locals import *
from sys import exit
import threading
import time
import ReinforceLearning as rl
import random

random.seed(time.time())
class GameThread(threading.Thread):

    screen_width = 640
    screen_height = 560

    line_num = 15
    width = 36

    piece_width = 18

    board_offset = [screen_width / 40, screen_height / 40]

    screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)

    color_dict = {-1: (255, 255, 255), 1: (0, 0, 0)}

    now_color = 1
    chess_board = [[0 for col in range(15)] for row in range(15)]

    history = []

    step_num = 0

    explore = 0.0001

    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.id = thread_id

    def loop(self):
        self.display()

        mouse_pos = [-1, -1]

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                # if event.type == MOUSEBUTTONUP:
                #     if event.button == 1:
                #         mouse_pos2 = self.get_xy(event.pos)
                #         if mouse_pos2 == mouse_pos and self.chess_board[mouse_pos[0]][mouse_pos[1]] == 0:
                #             self.chess_board[mouse_pos[0]][mouse_pos[1]] = self.now_color
                #             if self.is_win(mouse_pos[0], mouse_pos[1], self.now_color):
                #                 self.add_train_data()
                #                 self.init_board()
                #             self.history.append(self.copy_self())
                #             self.now_color = -self.now_color
                #             self.step_num += 1
                # if event.type == MOUSEBUTTONDOWN:
                #     if event.button == 1:
                #         mouse_pos = self.get_xy(event.pos)
            self.display()
            time.sleep(0.2)

    def run(self):
        time.sleep(1)
        num = 0
        while True:
            self.generate_data()
            print(rl.train_data['y'])
            rl.train()
            num += 1
            print("train num %d " % (num, ))

    def place_pieces(self, x, y):
        self.chess_board[x][y] = self.now_color
        if self.is_win(x, y, self.now_color):
            self.add_train_data()
            self.init_board()
            return
        self.history.append(self.copy_self())
        self.now_color = -self.now_color
        self.step_num += 1

    def copy_self(self):
        board_copy = [[0 for col in range(self.line_num)] for row in range(self.line_num)]
        length = len(self.chess_board)
        side = self.now_color
        for i in range(length):
            for j in range(length):
                board_copy[i][j] = side*self.chess_board[i][j]

        return board_copy

    def get_xy(self, pos):
        x = (pos[0] - self.board_offset[0] + self.width/2) / self.width
        y = (pos[1] - self.board_offset[1] + self.width/2) / self.width
        xy = (int(x), int(y))
        return xy

    def draw_piece(self, chess_color, pos):
        x = self.board_offset[0] + pos[0]*self.width
        y = self.board_offset[1] + pos[1]*self.width
        xy = (int(x), int(y))
        color_num = self.color_dict[chess_color]
        pygame.draw.circle(self.screen, color_num, xy, self.piece_width)

    def draw_board(self):
        self.screen.fill((100, 255, 100))
        for i in range(0, self.line_num):
            pygame.draw.line(self.screen, (0, 0, 0), (self.board_offset[0] + i * self.width, self.board_offset[1]),
                             (self.board_offset[0] + i * self.width,
                              self.board_offset[1] + (self.line_num - 1) * self.width))
            pygame.draw.line(self.screen, (0, 0, 0), (self.board_offset[0], self.board_offset[1] + i * self.width),
                             (self.board_offset[0] + (self.line_num - 1) * self.width,
                              self.board_offset[1] + i * self.width))

    def init_board(self):
        length = len(self.chess_board)
        for i in range(length):
            for j in range(length):
                self.chess_board[i][j] = 0

        self.history = []
        self.now_color = 1
        self.step_num = 0

    def display(self):
        pygame.init()
        self.draw_board()
        for i in range(len(self.chess_board)):
            for j in range(len(self.chess_board[i])):
                if self.chess_board[i][j] != 0:
                    self.draw_piece(self.chess_board[i][j], (i, j))
        pygame.display.update()

    def add_train_data(self):
        y = 0.5
        side = 1
        a = 0.5/self.step_num
        for i in range(self.step_num):
            y2 =y + a*side*(i+1)
            rl.train_data['x'].append(self.to_input(self.history[i]))
            rl.train_data['y'].append([y2, 1 - y2])
            side = -side

    def to_input(self, board):
        c = [[[0.0 for col in range(2)] for col in range(self.line_num)] for row in range(self.line_num)]
        length = len(board)
        for i in range(length):
            for j in range(length):
                if board[i][j] == 1:
                    c[i][j][0] = 1.0
                elif board[i][j] == -1:
                    c[i][j][1] = 1.0
        return c

    def is_win(self, i, j, color):
        length = len(self.chess_board)
        a = 5
        count = 1
        for x in range(1, a):
            tx = i - x
            ty = j
            if tx < 0 or tx >= length:
                break
            if self.chess_board[tx][ty] == color:
                count += 1
            else:
                break

        for x in range(1, a):
            tx = i + x
            ty = j
            if tx < 0 or tx >= length:
                break
            if self.chess_board[tx][ty] == color:
                count += 1
            else:
                break

        if count >= 5:
            return True

        count = 1
        for x in range(1, a):
            tx = i - x
            ty = j - x
            if tx < 0 or tx >= length:
                break
            if ty < 0 or ty >= length:
                break
            if self.chess_board[tx][ty] == color:
                count += 1
            else:
                break

        for x in range(1, a):
            tx = i + x
            ty = j + x
            if tx < 0 or tx >= length:
                break
            if ty < 0 or ty >= length:
                break
            if self.chess_board[tx][ty] == color:
                count += 1
            else:
                break

        if count >= 5:
            return True

        count = 1
        for x in range(1, a):
            tx = i
            ty = j - x
            if ty < 0 or ty >= length:
                break
            if self.chess_board[tx][ty] == color:
                count += 1
            else:
                break

        for x in range(1, a):
            tx = i
            ty = j + x
            if ty < 0 or ty >= length:
                break
            if self.chess_board[tx][ty] == color:
                count += 1
            else:
                break

        if count >= 5:
            return True

        count = 1
        for x in range(1, a):
            tx = i - x
            ty = j + x
            if tx < 0 or tx >= length:
                break
            if ty < 0 or ty >= length:
                break
            if self.chess_board[tx][ty] == color:
                count += 1
            else:
                break

        for x in range(1, a):
            tx = i + x
            ty = j - x
            if tx < 0 or tx >= length:
                break
            if ty < 0 or ty >= length:
                break
            if self.chess_board[tx][ty] == color:
                count += 1
            else:
                break

        if count >= 5:
            return True
        return False

    def generate_data(self, ):
        rl.train_data = {"x": [], "y": []}
        num = 10
        while len(rl.train_data['x']) < num:
            self.next_move()

    def next_move(self):
        p = self.get_next_move()
        self.place_pieces(p[0], p[1])

    def get_next_move(self, ):
        board = self.copy_self()
        board2 = self.to_input(board)
        index = 0
        max_value = -2
        max_position = [0, 0]
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 0:
                    board2[i][j][index] = 1
                    value = rl.get_value(board2)
                    if random.random() < self.explore:
                        value += 2
                    if value > max_value:
                        max_value = value
                        max_position = [i, j]
                    board2[i][j][index] = 0
        print(max_position[0], max_position[1], self.now_color, max_value)
        return max_position
