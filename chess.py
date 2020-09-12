"""
This is a simple command line chess application.
Please feel free to use, modify, or redistribute it however you wish. Although
some credit would be nice, it's not necessary.

Some of the more esoteric rules such as en-passent, or draw by 3x repetition 
are yet to be implemented and I cannot guarantee that I will implement them
in future.

Some cool features which would be nice to implement if you are so inclined are:
    [Sane]
    - Game store and load functionality
    - Draw/resign functionality
    - Removing the old board from the screen before redrawing
    - Missing rules (some listed above)
    - History of moves played displayed on screen
    - A game timer
    - Nicer art :)
    - Ability to load in various art styles
    [Insane/complex]
    - Playing against the computer
    - Networking functionality to play against other players

p.s. at time of writing this has only been tested on python 3.8.5 and likely
    contains several bugs.
"""

__author__ = "Patrick Sheppard"
__email__ = "patricksheppardd@gmail.com"
__contact__ = "https://patrick-sheppard.com"
__copyright__ = "None, do what you want with this code."
__license__ = None
__version__ = "1.0.0"
__date__ = "Sat 12 Sep 2020"

from math import floor, ceil
import time
import os
import sys

# Set to 0.001 or even 0.01 to get that retro feel.
PRINT_DELAY = 0

# If you change these, you also need to change the ASCII art
# for the pieces.
WIDTH = 10
HEIGHT = 5

class Board:
    """
    The board/game class.
    Handles displaying the board as well as user input.
    """

    def __init__(self):
        self.board = [None] * 64
        self.setupboard()
        # False for whites turn, true for blacks turn
        self.blackturn = False

    def run(self):
        os.system('clear')
        while True:
            self.displayboard()
            try:
                self.doinput()
            except SystemExit:
                self.displayboard()
                break

    def setupboard(self):
        """Setup pieces in the board array."""
        for i in range(8, 16):
            self.board[i] = Pawn(True)
            self.board[i + 40] = Pawn(False)

        self.board[0] = Rook(True)
        self.board[7] = Rook(True)
        self.board[56] = Rook(False)
        self.board[63] = Rook(False)

        self.board[1] = Knight(True)
        self.board[6] = Knight(True)
        self.board[57] = Knight(False)
        self.board[62] = Knight(False)

        self.board[2] = Bishop(True)
        self.board[5] = Bishop(True)
        self.board[58] = Bishop(False)
        self.board[61] = Bishop(False)

        self.board[3] = Queen(True)
        self.board[59] = Queen(False)

        self.board[4] = King(True)
        self.board[60] = King(False)

    def displayboard(self):
        """Renders the board line by line."""
        squareindex = 0
        for y in range(HEIGHT * 8):
            for x in range(WIDTH * 8):
                # The current square that the loop is in.
                squareindex = (floor(y / HEIGHT) * 8) + floor(x / WIDTH)

                # If the y value of the square coordinates is odd.
                yodd = int(floor(y / HEIGHT) % 2 != 0)
                piece = self.board[squareindex]
                if piece is not None:
                    # The index of the ASCII art to get.
                    index = (((y % HEIGHT) * WIDTH) + (x % WIDTH))
                    char = piece.getpiecechar(index)
                    # tilda is the noop of this ascii art format
                    # (aka: just display the square background here.)
                    if char != '~':
                        print(char, end='')
                    else:
                        self.squarebg(squareindex, yodd)
                else:
                    self.squarebg(squareindex, yodd)

                # Some cool time delay can be added.
                time.sleep(PRINT_DELAY)
                # Need to flush as there is no newline yet.
                sys.stdout.flush()

            # Display the numbers on the right hand side of the board.
            num = str(8 - floor(y / HEIGHT))
            if y % HEIGHT != 2:
                num = ''
            print('   ' + num)
        
        # Display letters at bottom of board.
        letters = (
            (' ' * 5) + 'A' + 
            (' ' * 9) + 'B' +            
            (' ' * 9) + 'C' + 
            (' ' * 9) + 'D' + 
            (' ' * 9) + 'E' + 
            (' ' * 9) + 'F' + 
            (' ' * 9) + 'G' + 
            (' ' * 9) + 'H'
        )
        print('\n' + letters)

    def squarebg(self, squareindex, yodd):
        """
        Prints the correct square background
        squareindex: the index of the square in the board array.
        yodd: True if the y coord of the square is odd.
        """
        if (squareindex + yodd) % 2 == 0:
            print(' ', end='')
        else:
            print(':', end='')

    def doinput(self):
        """Handles user input and moves the pieces."""
        print('\n')
        pieceinput = input('Piece->').strip().lower()

        fromcoords = self.validateposition(pieceinput)

        if not fromcoords:
            print('Invalid coordinates!')
            return
        
        piece = self.board[self.coordstoindex(fromcoords)]
        if piece is None or piece.black != self.blackturn:
            print('Invalid piece!')
            return

        position = input('To->').strip().lower()

        tocoords = self.validateposition(position)

        if not tocoords:
            print('Invalid coordinates!')
            return

        fromindex = self.coordstoindex(fromcoords)
        toindex = self.coordstoindex(tocoords)
        
        if not piece.validmove(self.board,fromindex,toindex):
            print('Invalid move!')
            return
        piece.move(self.board, fromindex, toindex)
        print(
            ('Black' if self.blackturn else 'White') +\
            ' moves ' + pieceinput + ' to ' + position + '. ' + \
            ('White' if self.blackturn else 'Black') + ' to play.')
        self.blackturn = not self.blackturn

    def validateposition(self, position):
        """
        Ensures that the board position input is valid (e.g. A1, H7, etc...).
        """
        letters = 'abcdefgh'
        y = None
        if 2 > len(position) or len(position) < 2:
            return False
        if position[0] not in letters:
            return False
        try:
            y = int(position[1])
            if y < 1 or y > 8:
                return False
        except ValueError:
            return False

        return letters.index(position[0]), y

    def coordstoindex(self, coords):
        """Converts 2 tuple/list to board array index."""
        # XXX This is possibly a bug, watch out.
        return coords[0] + ((8 - coords[1]) * 8)

class Piece:
    """
    The base piece class.
    Provides utility functions for checking validity of moves/game state 
    as well as basic implementations of functions such as move and validmove.
    """

    def __init__(self, black, name=''):
        # False for white, True for black.
        self.black = black
        self.name = name
        self.moved = False

    def getpiecechar(self, index):
        """
        Gets the character of the ASCII art to display on a grid of size 
        WIDTH x HEIGHT.
        """
        return art['black' if self.black else 'white'][self.name][index]

    def move(self, board, curr, to):
        """Basic movement. Move piece from 'curr' index to 'to' index."""
        board[curr] = None
        board[to] = self
        self.moved = True
        self.checkforchecks(board)

    def checkforchecks(self, board):
        """
        Decide if either check or checkmate conditions are at current
        board state.
        If checkmate then raises SystemExit which can/is caught upstream.
        """
        if self.checkmate(board):
            print('Checkmate!')
            print(('Black' if self.black else 'White') + ' Wins!')
            sys.exit(1)
        if self.kingchecked(board, not self.black):
            print('Check!')

    def moves(self, board, curr, allowspecial=True):
        """The valid moves that this piece can make."""
        return []

    def validmove(self, board, curr, to):
        """Decides if given move is a valid move using the moves() function."""
        if not self.notsame(curr, to) or self.movewillcheckownking(board, curr, to):
            return False

        moves = self.moves(board, curr)

        return self.indextocoords(to) in moves

    def indextocoords(self, index):
        """Convert a board array index to coordinate 2 tuple."""
        return index % 8, floor(index / 8)

    def coordstoindex(self, coords):
        """Convert a coordinate 2 tuple to a board array index."""
        return coords[0] + (coords[1] * 8)

    def validsquare(self, coords):
        """Decide if the coordinates are valid board coordinates."""
        return coords[0] in range(0, 8) and coords[1] in range(0,8)

    def emptysquare(self, board, coords):
        """Decide if given coordinates are empty."""
        return board[self.coordstoindex(coords)] is None
    
    def pieceat(self, board, coords):
        """Get the piece at the given coordinates."""
        return board[self.coordstoindex(coords)]

    def notsame(self, _from, to):
        """Check if from and to are not the same square."""
        return _from != to

    def walk(self, board, curr, stepx, stepy, limit=8):
        """
        Get list of moves from (not including) current board array index 
        to either edge of board, friendly piece (not including piece), or enemy 
        piece (including piece).
        Moves by (stepx, stepy) for every move up to limit.
        """
        moves = []
        coords = curr[0] + stepx, curr[1] + stepy
        while self.validsquare(coords):
            if limit == 0:
                break

            if not self.emptysquare(board, coords):
                if self.pieceat(board, coords).black is not self.black:
                    moves.append(coords)
                break
            moves.append(coords)
            coords = coords[0] + stepx, coords[1] + stepy

            limit -= 1

        return moves

    def allofcolor(self, board, black):
        """"Get all the pieces of either black if black == true or white."""
        pieces = []
        for piece in board:
            if piece is not None and piece.black is black:
                pieces.append(piece)
        return pieces

    def kingchecked(self, board, black):
        """Decied if the king is checked at the given board position."""
        enemy = self.allofcolor(board, not black)
        king = [piece for piece in self.allofcolor(board, black) if piece.name=='king'][0]
        kingcoords = self.indextocoords(board.index(king))
        enemyMoves = [
            move for piece in enemy
            for move in piece.moves(board, board.index(piece), allowspecial=False)
        ]
        return kingcoords in enemyMoves

    def movewillcheckownking(self, board, curr, to):
        """Decide if the given move will check this sides king."""
        toPositionOrig = board[to]
        board[curr] = None
        board[to] = self
        kingchecked = self.kingchecked(board, self.black)
        board[curr] = self
        board[to] = toPositionOrig
        return kingchecked

    def checkmate(self, board):
        """Decide if checkmate conditions have been reached."""
        for piece in self.allofcolor(board, not self.black):
            for move in piece.moves(board, board.index(piece)):
                if not piece.movewillcheckownking(board, board.index(piece), self.coordstoindex(move)):
                    return False
        return True

class Pawn(Piece):
    """Defines the mightiest piece on the board."""

    def __init__(self, *args):
        super().__init__(name='pawn', *args)

    def move(self, board, curr, to):
        promote = (not self.black and to < 8) or (self.black and to > 54)

        if promote:
            board[curr] = None
            board[to] = self.getpromotion()
            self.checkforchecks(board)
        else:
            super().move(board, curr, to)

    def getpromotion(self):
        while True:
            prompt = 'Promotion (1) Rook, (2) Knight, (3) Bishop, (4) Queen ->'
            value = input(prompt).strip()

            try:
                value = int(value)
                if value == 1:
                    return Rook(self.black)
                elif value == 2:
                    return Knight(self.black)
                elif value == 3:
                    return Bishop(self.black)
                elif value == 4:
                    return Queen(self.black)
                else:
                    raise ValueError
            except ValueError:
                print('Invalid promotion.')
                continue

    def moves(self, board, curr, allowspecial=True):
        moves = []
        mul = 1 if self.black else -1
        coords = self.indextocoords(curr)

        forwards1 = coords[0], (coords[1] + 1*mul)
        forwards2 = coords[0], (coords[1] + 2*mul)
        takeleft = (coords[0] + 1), (coords[1] + 1*mul)
        takeright = (coords[0] - 1), (coords[1] + 1*mul)

        if self.validsquare(forwards1) and self.emptysquare(board, forwards1):
            moves.append(forwards1)
            if self.validsquare(forwards2) and self.emptysquare(board, forwards2) and not self.moved:
                moves.append(forwards2)
        if self.validsquare(takeleft) and not self.emptysquare(board, takeleft) and self.pieceat(board, takeleft).black is not self.black:
            moves.append(takeleft)
        if self.validsquare(takeright) and not self.emptysquare(board, takeright) and self.pieceat(board, takeright).black is not self.black:
            moves.append(takeright)
        
        return moves

class Rook(Piece):

    def __init__(self, *args):
        super().__init__(name='rook', *args)

    def moves(self, board, curr, allowspecial=True):
        coords = self.indextocoords(curr)
        up = self.walk(board, coords, 0, -1)
        right = self.walk(board, coords, -1, 0)
        down = self.walk(board, coords, 0, 1)
        left = self.walk(board, coords, 1, 0)

        return up + right + down + left

class Knight(Piece):

    def __init__(self, *args):
        super().__init__(name='knight', *args)

    def moves(self, board, curr, allowspecial=True):
        coords = self.indextocoords(curr)
        moves = []
        
        upleft = coords[0] - 1, coords[1] - 2
        upright = coords[0] + 1, coords[1] - 2
        rightup = coords[0] + 2, coords[1] - 1
        rightdown = coords[0] + 2, coords[1] + 1
        downright = coords[0] + 1, coords[1] + 2
        downleft = coords[0] - 1, coords[1] + 2
        leftdown = coords[0] - 2, coords[1] + 1
        leftup = coords[0] - 2, coords[1] - 1

        potential = [upleft, upright, rightup, rightdown, downright, downleft, leftdown, leftup]

        for move in potential:
            if not self.validsquare(move):
                continue
            if not self.emptysquare(board, move):
                if self.pieceat(board, move).black is self.black:
                    continue
            moves.append(move)

        return moves

class Bishop(Piece):

    def __init__(self, *args):
        super().__init__(name='bishop', *args)

    def moves(self, board, curr, allowspecial=True):
        coords = self.indextocoords(curr)
        upleft = self.walk(board, coords, -1, -1)
        upright = self.walk(board, coords, 1, -1)
        downleft = self.walk(board, coords, -1, 1)
        downright = self.walk(board, coords, 1, 1)

        return upleft + upright + downleft + downright

class Queen(Piece):

    def __init__(self, *args):
        super().__init__(name='queen', *args)

    def moves(self, board, curr, allowspecial=True):
        coords = self.indextocoords(curr)

        up = self.walk(board, coords, 0, -1)
        upright = self.walk(board, coords, 1, -1)
        right = self.walk(board, coords, -1, 0)
        downright = self.walk(board, coords, 1, 1)
        down = self.walk(board, coords, 0, 1)
        downleft = self.walk(board, coords, -1, 1)
        left = self.walk(board, coords, 1, 0)
        upleft = self.walk(board, coords, -1, -1)

        return up + upright + right + downright + down + downleft + left + upleft

class King(Piece):

    def __init__(self, *args):
        super().__init__(name='king', *args)

    def move(self, board, curr, to):
        # Castle if king moves 2. Move is already validated by moves().
        if abs(curr - to) == 2:
            leftcastle = curr > to
            if leftcastle:
                rook = board[to - 2]
                board[to - 2] = None
                board[to + 1] = rook
            else:
                rook = board[to + 1]
                board[to + 1] = None
                board[to - 1] = rook
        super().move(board, curr, to)

    def moves(self, board, curr, allowspecial=True):
        coords = self.indextocoords(curr)

        castles = []
        if not self.moved and allowspecial:
            left = self.walk(board, coords, -1, 0)
            right = self.walk(board, coords, 1, 0)

            leftrook = self.pieceat(board, [0, coords[1]])
            rightrook = self.pieceat(board, [7, coords[1]])

            if len(left) == 3 and self.cancastlesafely(board, coords, left, leftrook):
                castles.append(left[1])
            if len(right) == 2 and self.cancastlesafely(board, coords, right, rightrook):
                castles.append(right[1])

        up = self.walk(board, coords, 0, -1, 1)
        upright = self.walk(board, coords, 1, -1, 1)
        right = self.walk(board, coords, -1, 0, 1)
        downright = self.walk(board, coords, 1, 1, 1)
        down = self.walk(board, coords, 0, 1, 1)
        downleft = self.walk(board, coords, -1, 1, 1)
        left = self.walk(board, coords, 1, 0, 1)
        upleft = self.walk(board, coords, -1, -1, 1)

        return up + upright + right + downright + down + downleft + left + upleft + castles

    def cancastlesafely(self, board, coords, moves, rook):
        if rook is None or rook.name != 'rook' or rook.moved:
            return False

        if self.movewillcheckownking(board, self.coordstoindex(coords), self.coordstoindex(moves[0])):
            return False
        if self.movewillcheckownking(board, self.coordstoindex(coords), self.coordstoindex(moves[1])):
            return False

        return True

art = {
    'black': {
        'pawn': (
            r'~~~~~~~~~~' +
            r'~~~~()~~~~' +
            r'~~~~)(~~~~' +
            r'~~~/@@\~~~' +
            r'~~~~~~~~~~'
        ),
        'rook': (
            r'~~~~~~~~~~' +
            r'~~|_||_|~~' +
            r'~~~|@@|~~~' +
            r'~~~|@@|~~~' +
            r'~~/@@@@\~~'
        ),
        'knight': (
            r'~~~~~~~~~~' +
            r'~~/^ ^\~~~' +
            r'~~\@@@@\~~' +
            r'~~|@@|\/~~' +
            r'~~/@@\~~~~'
        ),
        'bishop': (
            r'~~~~~~~~~~' +
            r'~~~~(/)~~~' +
            r'~~~~|@|~~~' +
            r'~~~~|@|~~~' +
            r'~~~/@@@\~~'
        ),
        'queen': (
            r'~~~WWWW~~~' +
            r'~~~)@@(~~~' +
            r'~~~|@@|~~~' +
            r'~~~|@@|~~~' +
            r'~~/@@@@\~~'
        ),
        'king': (
            r'~~~_++_~~~' +
            r'~~~)@@(~~~' +
            r'~~~|@@|~~~' +
            r'~~~|@@|~~~' +
            r'~~/@@@@\~~'
        ),
    },
    'white': {
        'pawn': (
            r'~~~~~~~~~~' +
            r'~~~~()~~~~' +
            r'~~~~)(~~~~' +
            r'~~~/__\~~~' +
            r'~~~~~~~~~~'
        ),
        'rook': (
            r'~~~~~~~~~~' +
            r'~~|_||_|~~' +
            r'~~~|  |~~~' +
            r'~~~|  |~~~' +
            r'~~/____\~~'
        ),
        'knight': (
            r'~~~~~~~~~~' +
            r'~~/^ ^\~~~' +
            r'~~\    \~~' +
            r'~~|  |\/~~' +
            r'~~/__\~~~~'
        ),
        'bishop': (
            r'~~~~~~~~~~' +
            r'~~~~(/)~~~' +
            r'~~~~| |~~~' +
            r'~~~~| |~~~' +
            r'~~~/___\~~'
        ),
        'queen': (
            r'~~~WWWW~~~' +
            r'~~~)  (~~~' +
            r'~~~|  |~~~' +
            r'~~~|  |~~~' +
            r'~~/____\~~'
        ),
        'king': (
            r'~~~_++_~~~' +
            r'~~~)  (~~~' +
            r'~~~|  |~~~' +
            r'~~~|  |~~~' +
            r'~~/____\~~'
        ),
    }
}

if __name__ == '__main__':
    Board().run()