import random
import math
import copy
from Rectangle import Rectangle

class Shikaku:
    def __init__(self, width, height, clues):
        # Largeur et hauteur de la grille
        self.width = width
        self.height = height
        # Clues : liste de tuples (x, y, value) avec la position et la valeur cible
        self.clues = clues
        # Liste initiale de rectangles générée aléatoirement
        self.rectangles = self.random_solution()

    def random_solution(self):
        # Pour chaque indice clue, on choisit un rectangle valide au hasard
        rects = []
        for x, y, value in self.clues:
            candidates = self.generate_rectangles(x, y, value)
            if candidates:
                rects.append(random.choice(candidates))
        return rects

    def generate_rectangles(self, x, y, value):
        # Génère tous les rectangles valides qui :
        # - contiennent la cellule (x, y)
        # - ont une surface égale à "value"
        # - restent dans les limites de la grille
        rects = []
        for w in range(1, value + 1):
            if value % w == 0: # w * h = value
                h = value // w
                for dx in range(w):
                    for dy in range(h):
                        x1 = x - dx
                        y1 = y - dy
                        x2 = x1 + w - 1
                        y2 = y1 + h - 1
                        # Vérifie que le rectangle reste dans la grille
                        if 0 <= x1 <= x2 < self.width and 0 <= y1 <= y2 < self.height:
                            rects.append(Rectangle(x1, y1, x2, y2, value))
        return rects

    def fitness(self):
        # ======================================================
        # METRIQUE DE QUALITE : Fonction "fitness"
        # Cette fonction évalue la qualité d'une solution partielle.
        # Objectif : fitness = 0 pour une grille parfaitement résolue
        # ======================================================
        penalty = 0
        # Penalité si l'aire d'un rectangle ne correspond pas à sa valeur
        for rect in self.rectangles:
            if rect.aire() != rect.value:
                penalty += 1

        # Penalité si une cellule n’est couverte par aucun ou plusieurs rectangles
        for y in range(self.height):
            for x in range(self.width):
                count = sum(1 for r in self.rectangles if r.contient(x, y))
                if count == 0:
                    penalty += 1
                elif count > 1:
                    penalty +=1
        # Penalité si deux rectangles se chevauchent
        for i in range(len(self.rectangles)):
            for j in range(i + 1, len(self.rectangles)):
                if self.rectangles[i].chevauche(self.rectangles[j]):
                    penalty += 1
        return penalty

    def voisin(self):
        # Retourne une solution voisine en modifiant un rectangle problématique
        new_grid = copy.deepcopy(self)

        # Évaluer les zones qui posent problème
        covered = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for rect in new_grid.rectangles:
            for y in range(rect.y1, rect.y2 + 1):
                for x in range(rect.x1, rect.x2 + 1):
                    covered[y][x] += 1

        # Trouver un rectangle problématique
        bad_indices = []
        for i, rect in enumerate(new_grid.rectangles):
            bad = False
            if rect.aire() != rect.value:
                bad = True
            for y in range(rect.y1, rect.y2 + 1):
                for x in range(rect.x1, rect.x2 + 1):
                    if covered[y][x] > 1:
                        bad = True
                        break
            if bad:
                bad_indices.append(i)

        # Sélection aléatoire si rien de mauvais trouvé
        idx = random.choice(bad_indices) if bad_indices else random.randint(0, len(new_grid.rectangles) - 1)
        x, y, val = self.clues[idx]
        candidates = self.generate_rectangles(x, y, val)
        if candidates:
            new_grid.rectangles[idx] = random.choice(candidates)

        return new_grid


# Fonction d’acceptation d’un voisin moins bon :
# On accepte avec une probabilité qui diminue avec dF et la température
def accept(dF, T):
        if dF > 0:
            A = math.exp(-dF / T)
            if random.random() >= A:
                return False
        return True

# Implémentation du recuit simulé pour résoudre Shikaku

def recuit_simulie(X0):
    X = X0  # Solution actuelle
    T = 1000  # plus c'est haut plus longtemps on peut remonter la courbe (diminue au fur et à mesure)
    Nt = 100  # nb d'itération
    alpha = 0.95 # Taux de refroidissement
    while X.fitness() != 0:  # Tant que la solution n’est pas parfaite
        for i in range(0, Nt):
            Y = X.voisin()
            dF = Y.fitness() -X.fitness()
            if accept(dF, T):
                X = Y
        T = T * alpha
    return X

def display_grid(grid):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, ax = plt.subplots()
    colors = plt.get_cmap('tab20')

    # Inverser l’axe Y pour que (0,0) soit en haut à gauche
    ax.set_xlim(0, grid.width)
    ax.set_ylim(grid.height, 0)

    # Afficher les rectangles
    for i, rect in enumerate(grid.rectangles):
        width = rect.x2 - rect.x1 + 1
        height = rect.y2 - rect.y1 + 1

        ax.add_patch(patches.Rectangle(
            (rect.x1, rect.y1),
            width,
            height,
            edgecolor='black',
            facecolor=colors(i % 20),
            linewidth=2
        ))

    # Ajouter les valeurs clues aux coordonnées exactes
    for (x, y, val) in grid.clues:
        ax.text(x + 0.5, y + 0.5, str(val),
                ha='center', va='center',
                color='black', fontsize=12, fontweight='bold')

    # Activer la grille et configurer les ticks
    ax.set_xticks(range(grid.width))
    ax.set_yticks(range(grid.height))

    # Ajouter les numéros d’axes (coordonnées)
    ax.set_xticklabels([str(i) for i in range(grid.width)])
    ax.set_yticklabels([str(i) for i in range(grid.height)])

    ax.grid(True)
    ax.set_aspect('equal')

    # Afficher la grille
    plt.title("Solution Shikaku")
    plt.show()


def read_grid(path):
    # Lit un fichier texte contenant :
    # ligne 1 : largeur hauteur
    # lignes suivantes : x y valeur
    with open(path, "r") as f:
        lines = f.readlines()
    width, height = map(int, lines[0].split())
    clues = []
    for line in lines[1:]:
        x, y, val = map(int, line.split())
        clues.append((y, x, val))
    return width, height, clues

if __name__ == '__main__':
    path = "..//grids//medium//250510"
    width, height, clues = read_grid(path)
    grid = Shikaku(width, height, clues)
    """ display_grid(grid) """

    print("Fitness initial:", grid.fitness())
    solution = recuit_simulie(grid)
    print("Fitness final:", solution.fitness())
    display_grid(solution)
