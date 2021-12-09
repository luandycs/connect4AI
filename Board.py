import numpy as np
import pygame
import sys
import math
import random
import ast


class Board:
    def __init__(self, board=np.zeros((6, 7))):
        # board parameters
        self.ROWS = 6
        self.COLUMNS = 7
        self.board = np.zeros((self.ROWS, self.COLUMNS))
        self.timer = 0

        # player settings
        self.HOST = 1
        self.AI = 2
        self.PLAYERS = [self.HOST, self.AI]
        self.turn = random.randint(0, 1)
        self.PLAYER = self.PLAYERS[self.turn]

        # pygame settings
        self.SQUARE_SIZE = 100
        self.w = self.COLUMNS * self.SQUARE_SIZE
        self.h = (self.ROWS+1) * self.SQUARE_SIZE
        self.GRID_SIZE = [self.w, self.h]
        pygame.font.init()
        self.FONT = pygame.font.SysFont('arial', 100)

    def move(self, board, r, c, player):
        board[r][c] = player

    # get/sets if needed
    def getPlayer(self):
        return self.PLAYER

    def getBoard(self):
        return self.board

    def getTurn(self):
        return self.turn

    def setBoard(self, board):
        self.board = board

    def setTurn(self, turn):
        self.turn = turn

    # Return: list of positions that contain '0' (open moves) at the lowest r value in each column
    # lastOpenRow can return NONE, need if to check
    def possibleMoves(self, board):
        moves = []
        for c in range(self.COLUMNS):
            r = self.lastOpenRow(board, c)
            if r == None:
                pass
            else:
                moves.append((r, c))
        return moves

    def nextTurn(self):
        if self.turn == 1:
            self.turn = 0
        else:
            self.turn = 1
        self.timer += 1

        ##### checks four in a row for wins #####
    def checkWin(self, board, player):
        # horizontal win
        # since horizontal win conditions require the middle of the board to be filled there is an if statement to check
        for r in range(self.ROWS):
            if board[r][3] == player:
                for c in range(self.COLUMNS-3):
                    if board[r][c] == player and board[r][c+1] == player and board[r][c+2] == player and board[r][c+3] == player:
                        return True
        # vertical win
        # since vertical win conditions require the middle of the board to be filled there is an if statement to check
        for c in range(self.COLUMNS):
            if board[3][c] == player:
                for r in range(self.ROWS-3):
                    if board[r][c] == player and board[r+1][c] == player and board[r+2][c] == player and board[r+3][c] == player:
                        return True
        # bottom to top diagonal win /
        for r in range(self.ROWS-3):
            for c in range(self.COLUMNS-3):
                if board[r][c] == player and board[r+1][c+1] == player and board[r+2][c+2] == player and board[r+3][c+3] == player:
                    return True
        # top to bottom diagonal win \
        for r in range(3, self.ROWS):
            for c in range(self.COLUMNS-3):
                if board[r][c] == player and board[r-1][c+1] == player and board[r-2][c+2] == player and board[r-3][c+3] == player:
                    return True
        return False

        # gets the next open slot for that column; if no more slots, returns NONE
    def lastOpenRow(self, board, c):
        for r in range(self.ROWS):
            if board[r][c] == 0:
                return r

    def scoreSection(self, pos, player):
        points = 0
        # WHOSE TURN ARE WE EVALUATING
        if player == self.HOST:
            oppPlayer = self.AI
        else:
            oppPlayer = self.HOST
            

        # ASSIGNING POINTS ACCORDING TO THE SITUATION IN A SPACE OF 4 SQUARES
        if pos.count(player) == 4:
            points += 25000000000
        elif pos.count(player) == 3 and pos.count(0) == 1:
            points += 18
        elif pos.count(player) == 2 and pos.count(0) == 2:
            points += 6
        
        
        if pos.count(oppPlayer) == 3 and pos.count(0) == 1:
            points -= 16
        elif pos.count(oppPlayer) == 3 and pos.count(player) == 1:
            points += 10    
        elif pos.count(oppPlayer) == 2 and pos.count(player) == 1:
            points += 2
        
        points -= (self.timer*2)
        return points

    # gives points for the board state in the POV of player arg
    def evaluateBoard(self, board, player):
        points = 0
        
        # bonus points for taking middle of the board
        centerCount = 0
        for r in range(self.ROWS):
            if board[r][3] == player:
                centerCount += 1
        points += centerCount * 3

        pos = []
        # gather all horizontal four in a row positions
        for r in range(self.ROWS):
            for c in range(self.COLUMNS-3):
                pos = []
                for i in range(4):
                    pos.append(board[r][c+i])
                points += self.scoreSection(pos, player)

        pos = []
        # gather all vertical four in a row positions
        for r in range(self.ROWS-3):
            for c in range(self.COLUMNS):
                pos = []
                for i in range(4):
                    pos.append(board[r+i][c])
                points += self.scoreSection(pos, player)

        pos = []
        # gather all four in a row / bottom to top diagonals
        for r in range(self.ROWS-3):
            for c in range(self.COLUMNS-3):
                pos = []
                for i in range(4):
                    pos.append(board[r+i][c+i])
                points += self.scoreSection(pos, player)

        pos = []
        # gather all four in a row \ top to bottom diagonals
        for r in range(self.ROWS-3):
            for c in range(self.COLUMNS-3):
                pos = []
                for i in range(4):
                    pos.append(board[r+3-i][c+i])
                points += self.scoreSection(pos, player)
        return points

    # checks for the situation of the game:
    # whether someone has won or there are no available moves left
    def gameEnd(self, board):
        if self.checkWin(board, self.HOST):
            return "HOST"
        if self.checkWin(board, self.HOST):
            return "AI"
        if len(self.possibleMoves(board)) == 0:
            return "DRAW"
        return False

    # Minmax algorithm to determine best move for AI PLAYER according to pseudocode given from wiki
    def predictMoves(self, board, depth, AIPLAYERTURN):
        possibilities = self.possibleMoves(board)
        gameEnd = self.gameEnd(board)
        col = None
        if gameEnd != False:
            if gameEnd == "HOST":
                return (col, -1000000)
            elif gameEnd == "AI":
                return (col, 1000000)
            else:
                return (col, 0)
        else:
            if depth == 0:
                return (None, self.evaluateBoard(board, self.AI))
            else:
                if AIPLAYERTURN == True:
                    value = -math.inf
                    col = random.choice(possibilities)[1]
                    for r, c in possibilities:
                        newBoard = board.copy()
                        self.move(newBoard, r, c, self.AI)
                        nextScore = self.predictMoves(newBoard, depth-1, False)[1]
                        if nextScore > value:
                            value = nextScore
                            col = c
                    
                else:
                    value = math.inf
                    col = random.choice(possibilities)[1]
                    for r, c in possibilities:
                        newBoard = board.copy()
                        self.move(newBoard, r, c, self.HOST)
                        nextScore = self.predictMoves(newBoard, depth-1, True)[1]
                        if nextScore < value:
                            value = nextScore
                            col = c
        return (col, value)
    # gives the best column to move in
    # used as basis for Minmax

    
    def bestMove(self, board, player):
        possbilities = self.possibleMoves(board)
        highscore = 0
        col = random.choice(possbilities)[1]
        for r, c in possbilities:
            newBoard = self.board.copy()
            self.move(newBoard, r, c, player)
            score = self.evaluateBoard(board, player)
            if score > highscore:
                highscore = score
                col = c
        return col

    # displays the game with red as the host player and yellow as the AI

    def draw(self):
        screen = pygame.display.set_mode(self.GRID_SIZE)

        for r in range(self.ROWS):
            for c in range(self.COLUMNS):
                pygame.draw.rect(screen, (0, 0, 255), (c*self.SQUARE_SIZE, r *
                                                       self.SQUARE_SIZE+self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))
                pygame.draw.circle(screen, (255, 255, 255), (int(c*self.SQUARE_SIZE+self.SQUARE_SIZE/2), int(
                    r*self.SQUARE_SIZE+self.SQUARE_SIZE+self.SQUARE_SIZE/2)), int(self.SQUARE_SIZE/2 - 5))
        for r in range(self.ROWS):
            for c in range(self.COLUMNS):
                if self.board[r][c] == self.HOST:
                    pygame.draw.circle(screen, (255, 0, 0), (int(c*self.SQUARE_SIZE+self.SQUARE_SIZE/2),
                                                             self.h - int(r*self.SQUARE_SIZE+self.SQUARE_SIZE/2)), int(self.SQUARE_SIZE/2 - 5))
                if self.board[r][c] == self.AI:
                    pygame.draw.circle(screen, (0, 255, 0), (int(c*self.SQUARE_SIZE+self.SQUARE_SIZE/2),
                                                             self.h - int(r*self.SQUARE_SIZE+self.SQUARE_SIZE/2)), int(self.SQUARE_SIZE/2 - 5))
        pygame.display.update()

        # starts the game
    def start(self):
        screen = pygame.display.set_mode(self.GRID_SIZE)
        print(np.flip(self.board, 0))
        pygame.init()
        self.draw()
        IN_PROGRESS = True

        while IN_PROGRESS:
            self.PLAYER = self.PLAYERS[self.turn]
            for action in pygame.event.get():

                if action.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (0, 0, self.w, self.SQUARE_SIZE))
                    x = action.pos[0]

                    if self.PLAYER == self.HOST:
                        pygame.draw.circle(screen, (255, 0, 0), (x, int(
                            self.SQUARE_SIZE/2)), int(self.SQUARE_SIZE/2 - 5))

                pygame.display.update()

                if action.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (0, 0, self.w, self.SQUARE_SIZE))

                    if self.PLAYER == self.HOST:
                        x = action.pos[0]
                        c = int(math.floor(x/self.SQUARE_SIZE))
                        if self.board[5][c] == 0:
                            r = self.lastOpenRow(self.board, c)
                            self.move(self.board, r, c, self.HOST)

                            if self.checkWin(self.board, self.HOST) == True:
                                label = self.FONT.render(
                                    "PLAYER WINS", 1, (255, 255, 255))
                                screen.blit(label, (40, 10))
                                IN_PROGRESS = False
                            print(np.flip(self.board, 0))
                            self.draw()
                            self.nextTurn()
                if action.type == pygame.QUIT:
                    sys.exit()

            if self.PLAYER == self.AI and IN_PROGRESS == True:
                c, minmaxScore = self.predictMoves(self.board, 4, True)
                r = self.lastOpenRow(self.board, c)

                if self.board[r][c] == 0:
                    self.move(self.board, r, c, self.AI)
                    if self.checkWin(self.board, self.AI) == True:
                        label = self.FONT.render("AI WINS", 1, (255, 255, 255))
                        screen.blit(label, (40, 10))
                        IN_PROGRESS = False
                print(np.flip(self.board, 0))
                self.draw()
                self.nextTurn()
            if IN_PROGRESS == False:
                pygame.time.wait(1000)

        pygame.time.wait(3000)
