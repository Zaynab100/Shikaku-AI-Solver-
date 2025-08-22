# ============================================
# CLASSE Rectangle : représentation de base du problème
# ============================================
class Rectangle:
    def __init__(self, x1, y1, x2, y2, value):
        # Un rectangle est défini par ses coins opposés (x1, y1) en haut à gauche et (x2, y2) en bas à droite
        # La valeur correspond au chiffre dans la case : elle indique la surface que le rectangle doit couvrir
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.value = value

    def aire(self):
        # Calcule l'aire réelle du rectangle
        return (self.x2 - self.x1 + 1) * (self.y2 - self.y1 + 1)

    def contient(self, x, y):
        # Vérifie si la case (x, y) est à l'intérieur du rectangle
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def chevauche(self, other):
        # Vérifie si deux rectangles se chevauchent
        return not (self.x2 < other.x1 or self.x1 > other.x2 or self.y2 < other.y1 or self.y1 > other.y2)

