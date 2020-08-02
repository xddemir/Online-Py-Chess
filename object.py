class GameState:
    def __init__(self):
        self.board =[
            ["br", "bkn","bb","bq","bk","bb", "bkn", "br"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"], 
            ["--", "--", "--","--", "--", "--","--", "--"],
            ["--", "--", "--","--", "--", "--","--", "--"],
            ["--", "--", "--","--", "--", "--","--", "--"],
            ["--", "--", "--","--", "--", "--","--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wr", "wkn", "wb", "wq", "wk", "wb", "wkn", "wr"]]

        self.piecesMove = {
                'p': self.getPownMoves,
                'r': self.getRockMoves,
                'kn': self.getKnightMoves,
                'b': self.getBishopMoves,
                'q': self.getQueenMoves,
                'k': self.getKingMoves}

        self.whiteToMoveOn = True
        self.moveLog = []
        self.whiteKingCord = (7, 4)
        self.blackKingCord = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # coordinates for square where en passant is possible 
        # castling class
        self.currentCastlingRight = CastlinRights(True, True, True, True)
        # undo castling
        self.castleRightLog = [CastlinRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
         self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, Move):
        # move
        self.board[Move.startRow][Move.startColumn] = "--"
        self.board[Move.endRow][Move.endColumn] = Move.piecesMove
        self.moveLog.append(Move)# log the move so we can undo it later        
        self.whiteToMoveOn = not self.whiteToMoveOn

        if Move.piecesMove == 'wk': # update whiteking location
            self.whiteKingCord = (Move.endRow, Move.endColumn)
        elif Move.piecesMove == 'bk': # update blacking location
            self.blackKingCord = (Move.endRow, Move.endColumn)
        
        # pawn promotion
        if Move.isPromoted():
            self.board[Move.endRow][Move.endColumn] = Move.piecesMove[0] + 'q'

        # en passant move
        if Move.isEnpassan:
            self.board[Move.startRow][Move.endColumn] = '--' # capturing the pawn

        # update enpossantPossible variable
        if Move.piecesMove[1] == 'p' and abs(Move.startRow - Move.endRow) == 2:
            self.enpassantPossible = ((Move.startRow + Move.endRow)//2, Move.startColumn)
        else:
            self.enpassantPossible = ()
        if Move.isCastleMove:
            if Move.endColumn - Move.startColumn == 2: # kingside castle move
                self.board[Move.endRow][Move.endColumn-1] = self.board[Move.endRow][Move.endColumn+1] # move the rook
                self.board[Move.endRow][Move.endColumn+1] = '--'
            else: # queenside
                self.board[Move.endRow][Move.endColumn+1] = self.board[Move.endRow][Move.endColumn-2] # move the rook
                self.board[Move.endRow][Move.endColumn-2] = '--'
        # update castling rights - whenever rook or king move
        self.UpdateCastlingRight(Move)
        self.castleRightLog.append(CastlinRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    def undoMove(self):
        if len(self.moveLog) != 0: # it means player've moved.
            move = self.moveLog.pop() # stack class
            #  pieces move and capture moves changes last positions 
            self.board[move.startRow][move.startColumn] = move.piecesMove  
            self.board[move.endRow][move.endColumn] = move.captureMove
            self.whiteToMoveOn = not self.whiteToMoveOn
            
            if move.piecesMove == 'wk': # undo whiteking location
                self.whiteKingCord = (move.startRow, move.startColumn)
            elif move.piecesMove == 'bk': # undo blacking location
                self.blackKingCord = (move.startRow, move.startColumn)

            if move.isEnpassan:
                self.board[move.endRow][move.endColumn] = '--' # leave landing square back
                self.board[move.startRow][move.endColumn] = move.captureMove
                self.enpassantPossible = (move.endRow, move.endColumn)
            #undo two squares pawn 
            if move.piecesMove[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            # undo castling
            self.castleRightLog.pop()
            self.currentCastlingRight = self.castleRightLog[-1]

            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2: # kingside
                    self.board[move.endRow][move.endColumn+1] = self.board[move.endRow][move.endColumn-1]
                    self.board[move.endRow][move.endColumn-1] = '--'
                else: # queenside
                    self.board[move.endRow][move.endColumn-2] = self.board[move.endRow][move.endColumn+1]
                    self.board[move.endRow][move.endColumn-2] = '--'

    def UpdateCastlingRight(self, move):
        if move.piecesMove == 'wk':
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.piecesMove == 'bk':
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.piecesMove == 'wr':
            if move.startRow == 7:
                if move.startColumn == 0: # left rock
                    self.currentCastlingRight.wqs = False
                elif move.startColumn == 7: # right rock
                    self.currentCastlingRight.wks = False
        elif move.piecesMove == 'br':
            if move.startRow == 0:
                if move.startColumn == 0: # left rock
                    self.currentCastlingRight.bqs = False
                elif move.startColumn == 7: # right rock
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastlingMove = CastlinRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
         self.currentCastlingRight.wqs, self.currentCastlingRight.bqs) # copy current castling
        
        moves = self.CheckPossibleMoves()
        # for castling
        if self.whiteToMoveOn:
            self.getCastleMoves(self.whiteKingCord[0], self.whiteKingCord[1], moves)
        else:
            self.getCastleMoves(self.blackKingCord[0], self.blackKingCord[1], moves)

        for i in range(len(moves)-1, -1, -1): # when removing line from a list go backwards through that list
            self.makeMove(moves[i])
            self.whiteToMoveOn = not self.whiteToMoveOn
            if self.inCheck():
                moves.remove(moves[i]) # if they do attack your king, not a valid move
            self.whiteToMoveOn = not self.whiteToMoveOn
            self.undoMove()
        if len(moves) == 0: # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastlingMove
        
        return moves
    
    """ determine current player is in check"""
    def inCheck(self):
        if self.whiteToMoveOn:
            return self.squareUnderAttack(self.whiteKingCord[0], self.whiteKingCord[1])
        else:
            return self.squareUnderAttack(self.blackKingCord[0], self.blackKingCord[1])

    """determine if the enemy can attack the square r, c """
    def squareUnderAttack(self, r, c):
        self.whiteToMoveOn = not self.whiteToMoveOn
        oppMoves = self.CheckPossibleMoves()
        self.whiteToMoveOn = not self.whiteToMoveOn
        for move in oppMoves:
            if move.endRow == r and move.endColumn == c: # square is under attack
                return True
        return False

    def CheckPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # rows of board
            for c in range(len(self.board[r])): # colums of board in given row 
               turn = self.board[r][c][0] # it gives first letter of the word
               if (turn == 'w' and self.whiteToMoveOn) or (turn == 'b' and not self.whiteToMoveOn):
                    piece = self.board[r][c][1:] # second letter of the word
                    self.piecesMove[piece](r, c, moves)
        return moves

    def getPownMoves(self, r, c, moves):
        if self.whiteToMoveOn: #white pawn
            if self.board[r-1][c] == "--": # one square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": # two square pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: # capture to the left place.
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                     moves.append(Move((r, c), (r-1, c-1), self.board, enpassanMove = True))

            if c + 1 <=7: # capture to the right place.
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c),(r-1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c),(r-1, c+1), self.board, enpassanMove= True))
            
        else: #black pawn
            if self.board[r+1][c] == '--':
                moves.append(Move((r, c), (r+1, c), self.board)) # drag one square ahead
                if r == 1 and self.board[r + 2][c] == '--':
                    moves.append(Move((r, c), (r+2, c), self.board)) # drag two square ahead
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, enpassanMove = True))
            if c+1 <=7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, enpassanMove = True))

    def getRockMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        color = 'b' if self.whiteToMoveOn else 'w'
        for d in directions:
            for i in range(1, 8):
                endrow = r + d[0] * i
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8:
                    endPiece = self.board[endrow][endcol]
                    if endPiece == '--':
                        moves.append(Move((r, c), (endrow, endcol), self.board))
                    elif endPiece[0] == color:
                        moves.append(Move((r, c), (endrow, endcol), self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # off board
                    break

    def getKnightMoves(self, r , c , moves):
        def knightMove(obj):
            """
            It's solved with a tricky way(hardCoding) in this reason it's gonna be improved later 
            """
            if r-2>=0:
                if self.board[r-2][c-1] == '--' or self.board[r-2][c-1][0] == obj:
                    moves.append(Move((r, c), (r-2, c-1), self.board))
                if c+1 <=7:
                    if self.board[r-2][c+1] == '--' or self.board[r-2][c+1][0] == obj:
                        moves.append(Move((r, c), (r-2, c+1), self.board))

            if c+2 <=7:
                if self.board[r-1][c+2] == '--' or self.board[r-1][c+2][0] == obj:
                    moves.append(Move((r, c), (r-1, c+2), self.board))
                if r + 1 <=7: 
                    if self.board[r+1][c+2] == '--' or self.board[r+1][c+2][0] == obj:
                        moves.append(Move((r, c), (r+1, c+2), self.board))

            if r+2 <= 7:
                if self.board[r+2][c-1] == '--' or  self.board[r+2][c-1][0] == obj:
                    moves.append(Move((r, c), (r+2, c-1), self.board))
                if c+1 <=7:
                    if self.board[r+2][c+1] == '--' or self.board[r+2][c+1][0] == obj:
                        moves.append(Move((r, c), (r+2, c+1), self.board))

            if c - 2 >= 0:
                if self.board[r-1][c-2] == "--" or self.board[r-1][c-2][0] == obj:
                    moves.append(Move((r, c), (r-1, c-2), self.board))
                if r+1 <=7:
                    if self.board[r+1][c-2] == '--' or self.board[r+1][c-2][0] == obj:
                        moves.append(Move((r, c), (r+1, c-2), self.board))

        if self.whiteToMoveOn:
            knightMove("b")
        else:
            knightMove("w")

    """ Generate all valid castle moves for the king (r, c) and add them to the list of moves """
    def getCastleMoves(self, r, c, moves):
        if self.inCheck(): # first step is whether the king is under attack nor
            return # can't castle while we are under attack by
        if (self.whiteToMoveOn and self.currentCastlingRight.wks) or (not self.whiteToMoveOn and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)

        if (self.whiteToMoveOn and self.currentCastlingRight.wqs) or (not self.whiteToMoveOn and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)
    # ROCK
    def getKingsideCastleMoves(self, r, c, moves): 
        # second rule is are there empty spaces between king and rock
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            # is square under attack
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):   
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))
    # ROCK            
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3]:
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove = True))
            
    def getBishopMoves(self, r, c, moves):
        direction = ((1, 1), (-1, -1), (1, -1), (-1, 1))
        color = 'b' if self.whiteToMoveOn else 'w'
        for d in direction:
            for i in range(1, 8):
                endrow = r + d[0] * i 
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8:
                    endPiece = self.board[endrow][endcol]
                    if endPiece == '--':
                        moves.append(Move((r, c), (endrow, endcol), self.board))
                    elif endPiece[0] == color:
                        moves.append(Move((r, c), (endrow, endcol), self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # off board
                    break

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c ,moves)
        self.getRockMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        def KingMove(color):
            """  it's gonna be updated later but still working """
            if self.board[r-1][c-1] == '--' or self.board[r-1][c-1][0] == color: # right cross
                moves.append(Move((r, c), (r-1, c-1), self.board))

            if c+1 <=7:
                if self.board[r-1][c+1] == '--' or self.board[r-1][c+1][0] == color: # left cross
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                if self.board[r][c+1] == '--' or self.board[r][c+1][0] == color: # right
                    moves.append(Move((r, c), (r, c+1), self.board))

            if self.board[r-1][c] == '--' or self.board[r-1][c][0] == color: # move straight
                moves.append(Move((r, c), (r-1, c), self.board))

            if self.board[r][c-1] == '--' or self.board[r][c-1][0] == color: # left
                moves.append(Move((r, c), (r, c-1), self.board))
           
            # to turn back
            if r+1 <=7:
                if self.board[r+1][c] == '--' or self.board[r+1][c][0] == color: 
                    moves.append(Move((r, c), (r+1, c), self.board))
                if self.board[r+1][c-1] == '--' or self.board[r+1][c-1][0] == color:
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                if c+1<=7:
                    if self.board[r+1][c+1] == '--' or self.board[r+1][c+1][0] == color:
                        moves.append(Move((r, c), (r+1, c+1), self.board))
        if self.whiteToMoveOn:
            KingMove('b')
        else:
            KingMove('w')



class CastlinRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move: 
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                    "5": 3, "6": 2, "7": 1,  "8": 0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                    "e": 4, "f": 5, "g": 6,  "h": 7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self, startsq, endsq, board, enpassanMove = False, isCastleMove = False):
        self.startRow = startsq[0] # 1
        self.startColumn = startsq[1] # 0
        self.endRow = endsq[0] # 0
        self.endColumn = endsq[1] # 2
        self.piecesMove = board[self.startRow][self.startColumn] # 'wp'
        self.captureMove = board[self.endRow][self.endColumn] # '--'
        # pawn promotion 
        self.isPawnPromotion = False
        # id 
        self.MoveID = self.startRow  * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn # unuqie id for moving
        #(1,0)  --> (2,0)

        # en passan
        self.isEnpassan = enpassanMove
        if self.isEnpassan:
            self.captureMove = 'wp' if self.piecesMove == 'bp' else 'bp'

        # castle move
        self.isCastleMove = isCastleMove

    def isPromoted(self): # it checks whether pawn is promoted
        if (self.piecesMove == 'wp' and self.endRow == 0) or (self.piecesMove == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True
            return self.isPawnPromotion

     # overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.MoveID == other.MoveID
        return False

    def getChessNotation(self):
        # you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startColumn) + self.getRankFile(self.endRow, self.endColumn) # 0cb3

    def getRankFile(self, r, c):
        return self.rowsToRanks[r] + self.colsToFiles[c]
