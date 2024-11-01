# ========================================================================================================
"""PENTE : implementation of the "Penté" board game for two players"""
# ========================================================================================================
__author__  = "MOIELWAY_TANOH_EZIN"
__version__ = "0.0" # skeleton version
__date__    = "2024-01-06"
# ========================================================================================================
from ezTK import*
# ========================================================================================================
class ConfigWin(Win):
    def __init__(self):
        Win.__init__(self, title='PENTE', grow=False, op=2)
        Label(self, text='CONFIGURATION', grow=False, height=2, width=45, anchor='C', bg='#000',fg='#FFF')
        frame=Frame(self, grow=False,fold=2) 
        Label(frame, text='Name of Player A :', width=20, anchor='E')
        self.playerA_name = Entry(frame, width=20)
        Label(frame, text='Name of Player B :', width=20, anchor='E')
        self.playerB_name = Entry(frame, width=20)

        Label(frame, text='Board Dimension  :', width=20, anchor='E')
        self.board_dim = Scale(frame, scale=(8, 16), length=200, flow='W')
        Label(frame, text='Score of Victory :', width=20, anchor='E')
        self.victory_score = Scale(frame, scale=(5, 15), length=200, flow='W')

        Button(self, text='START', command=self.start_game, bg='#000', fg='#FFF')

        self.loop()

    def start_game(self):
        playerA = self.playerA_name.state
        playerB = self.playerB_name.state
        dim = self.board_dim.state
        score = self.victory_score.state
        self.exit()
        GameWin(playerA, playerB, dim, score)


class GameWin(Win):
    def __init__(self, playerA_name, playerB_name, dim, victory_score):
        Win.__init__(self, title='PENTE', grow=False, op=2)

        self.images = ImageGrid('pente.png', 1, 4)  # on a 4 états distincts : vide, bleu, vert, gris
        self.current_player = 1  # Joueur A commence
        self.victory_score = victory_score  # Ajout du score de la victoire

        # Ajout des scores pour chaque joueur
        self.score_playerA = 0
        self.score_playerB = 0

        frame = Frame(self,border=2, bg='white', grow=False, flow='WE')
        self.label_playerA = Label(frame, text=f'{playerA_name}\n0',  width=20, anchor='E', bg='white', fg='black')
        self.label_turn = Label(frame, text=playerA_name, width=10, anchor='C', bg='black', fg='white')
        self.label_playerB = Label(frame, text=f'{playerB_name}\n0', width=20, anchor='W', bg='white', fg='black')

        frame = Frame(self, fold=dim, border=1)
        self.brick = [[Brick(frame, image=self.images[0], border=1) for _ in range(dim)] for _ in range(dim)]

        for row in range(dim):
            for col in range(dim):
                brick = self.brick[row][col]
                brick.bind('<Button-1>', lambda event, r=row, c=col: self.click(r, c))

        self.game = Game(dim)
        self.names = {1: playerA_name, 2: playerB_name}

    def victory_2(self, player, is_final_victory):
        if is_final_victory:
            winner = self.names[player]
            victory_window = tk.Toplevel(self)
            victory_window.title("Victoire !")
            victory_window.geometry("300x150")
            tk.Label(victory_window, text=f'Le joueur {winner} a gagné !\nVoulez-vous rejouer ?').pack(pady=10)
            tk.Button(victory_window, text="Quitter",
                      command=lambda: [victory_window.destroy(), self.exit(), ConfigWin()]).pack(side=tk.LEFT, padx=20,
                                                                                                 pady=10)
            tk.Button(victory_window, text="Continuer",
                      command=lambda: [victory_window.destroy(), self.master.quit()]).pack(side=tk.RIGHT, padx=20,
                                                                                           pady=10)
        else:
            Dialog('info', title='Point marqué !', message=f'Joueur {self.names[player]} a marqué des points !')

    def update_score(self, player, points):
        if player == 1:
            self.score_playerA += points
            self.label_playerA['text'] = f'{self.names[1]}\n{self.score_playerA}'
            if self.score_playerA >= self.victory_score:
                self.victory_2(player, True)
            elif points > 0:
                self.victory_2(player, False)
        else:
            self.score_playerB += points
            self.label_playerB['text'] = f'{self.names[2]}\n{self.score_playerB}'
            if self.score_playerB >= self.victory_score:
                self.victory_2(player, True)
            elif points > 0:
                self.victory_2(player, False)

    def click(self, row, col):
        if self.game.play(row, col, self.current_player):
            captures = self.game.check_and_perform_capture(row, col, self.current_player)
            if captures > 0:
                self.update_score(self.current_player, captures)

            alignment_found = self.game.align(row, col, self.current_player)
            if alignment_found:
                self.update_score(self.current_player, 5)

            self.update_display()  # Mise à jour de l'affichage après chaque action
            self.current_player = 3 - self.current_player
            self.label_turn['text'] = self.names[self.current_player]

    def update_display(self):
        for row in range(self.game.dim):
            for col in range(self.game.dim):
                cell_state = self.game.board[row][col]
                self.brick[row][col]['image'] = self.images[cell_state]
# Classe pour la logique du jeu "Penté"
class Game:
    def __init__(self, dim=8):
        self.dim = dim
        self.board = [[0 for _ in range(dim)] for _ in range(dim)]

    def play(self, row, column, player):
        if self.board[row][column] == 0:
            self.board[row][column] = player
            return True
        return False

    def align(self, row, col, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)] # les tuples represente chaque avancée dans une direction
        for dx, dy in directions:
            count = 0
            pieces_to_remove = []
            for i in range(-4, 5):
                x, y = row + i * dx, col + i * dy
                if 0 <= x < self.dim and 0 <= y < self.dim:
                    if self.board[x][y] == player:
                        count += 1
                        pieces_to_remove.append((x, y))
                        if count == 5:
                            self.remove_alignment(pieces_to_remove)
                            return True
                    else:
                        count = 0
                        pieces_to_remove = []
        return False

    def remove_alignment(self, pieces):
        for x, y in pieces:
            self.board[x][y] = 0

    def display_board(self):
        for row in self.board:
            print(' '.join(str(cell) for cell in row))
        print()

    def capture(self, row, col, player):
        captures = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        opponent = 4 - player

        for dx, dy in directions:
            for sign in [-1, 1]:  # Vérifier dans les deux sens pour chaque direction
                x, y = row + sign * dx, col + sign * dy
                if 0 <= x < self.dim and 0 <= y < self.dim:
                    if 0 <= x + 1 * dx < self.dim and 0 <= y + 1 * dy < self.dim:
                        if (self.board[x][y] == opponent and
                                self.board[x + dx][y + dy] == opponent and
                                self.board[x + 2 * dx][y + 2 * dy] == player):
                            # Retirer les pions adverses
                            self.board[x][y] = 0
                            self.board[x + dx][y + dy] = 0
                            captures += 2
        return captures

    def check_and_perform_capture(self, row, col, player):
        return self.capture(row, col, player)


if __name__ == "__main__":
    ConfigWin()

