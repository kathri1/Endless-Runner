import pygame
import random
import sys

# --- Einstellungen ---
BREITE, HOEHE = 800, 400
FPS = 60
SCHWERKRAFT = 0.6
SPRUNG_KRAFT = -13
BODEN_Y = 320

# Farben
HIMMEL    = (20,  20,  35)
BODEN_F   = (50,  50,  80)
SPIELER_F = (80, 200, 255)
SPIELER_DUCK = (60, 160, 220)
HINDERNIS = (255,  80,  80)
FLUG_F    = (255, 180,  50)
WOLKE_F   = (60,  60,  90)
WEISS     = (220, 220, 255)
GELB      = (255, 220,  60)

pygame.init()
screen = pygame.display.set_mode((BREITE, HOEHE))
pygame.display.set_caption("Endless Runner – Ebenen & Plattformen")
clock = pygame.time.Clock()
font      = pygame.font.SysFont("monospace", 28, bold=True)
font_gross = pygame.font.SysFont("monospace", 48, bold=True)


# ──────────────────────────────────────────
# Hilfsklassen
# ──────────────────────────────────────────

class Spieler:
    BREITE       = 40
    HOEHE_NORMAL = 50
    HOEHE_DUCK   = 25

    def __init__(self):
        self.reset()

    def reset(self):
        self.x              = 120
        self.y              = float(BODEN_Y - self.HOEHE_NORMAL)
        self.vy             = 0.0
        self.am_boden       = True
        self.sprung_zaehler = 0
        self.duckt          = False

    @property
    def HOEHE(self):
        return self.HOEHE_DUCK if self.duckt else self.HOEHE_NORMAL

    def springe(self):
        if self.sprung_zaehler < 2:
            self.vy = SPRUNG_KRAFT
            self.am_boden = False
            self.sprung_zaehler += 1

    def update(self, duckt, plattformen):
        # Füße sollen beim Ducken an der gleichen Stelle bleiben
        unten_vorher = self.y + self.HOEHE

        # Ducken nur, wenn vorher am Boden/Plattform
        self.duckt = duckt and self.am_boden

        # Höhe ändert sich -> y so anpassen, dass die Füße gleich bleiben
        self.y = unten_vorher - self.HOEHE

        # Physik
        self.vy += SCHWERKRAFT
        self.y  += self.vy

        # Plattform-Kollision
        self.am_boden = False
        for p in plattformen:
            r = p.rect()
            if (self.x + self.BREITE > r.left and
                self.x < r.right and
                self.y + self.HOEHE >= r.top and
                self.y + self.HOEHE <= r.top + 20 and
                self.vy >= 0):
                self.y = r.top - self.HOEHE
                self.vy = 0
                self.am_boden = True
                self.sprung_zaehler = 0

        # Boden-Kollision
        boden = BODEN_Y - self.HOEHE
        if self.y >= boden:
            self.y = float(boden)
            self.vy = 0
            self.am_boden = True
            self.sprung_zaehler = 0


    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.BREITE, self.HOEHE)

    def zeichne(self, surf):
        r = self.rect()
        farbe = SPIELER_DUCK if self.duckt else SPIELER_F
        pygame.draw.rect(surf, farbe, r, border_radius=8)
        auge_y = r.top + (8 if self.duckt else 12)
        pygame.draw.circle(surf, WEISS,  (r.left + 10, auge_y), 5)
        pygame.draw.circle(surf, WEISS,  (r.left + 28, auge_y), 5)
        pygame.draw.circle(surf, (0,0,0),(r.left + 12, auge_y), 3)
        pygame.draw.circle(surf, (0,0,0),(r.left + 30, auge_y), 3)
        if self.sprung_zaehler == 1 and not self.am_boden:
            pygame.draw.circle(surf, GELB, (r.centerx, r.top - 8), 5)


class Plattform:
    def __init__(self, geschwindigkeit):
        self.breite = random.randint(120, 200)
        self.hoehe = 18
        self.x = float(BREITE + 40)
        self.y = random.choice([240, 180, 120])
        self.speed = geschwindigkeit

    def update(self):
        self.x -= self.speed

    def rect(self):
        return pygame.Rect(int(self.x), self.y, self.breite, self.hoehe)

    def zeichne(self, surf):
        pygame.draw.rect(surf, (90, 90, 140), self.rect(), border_radius=6)


class Hindernis:
    def __init__(self, geschwindigkeit, plattform=None):
        self.breite = random.randint(20, 35)
        self.hoehe  = random.randint(30, 60)
        self.x      = float(BREITE + 20)
        self.speed  = geschwindigkeit

        if plattform:
            self.y = plattform.y - self.hoehe
        else:
            self.y = BODEN_Y - self.hoehe

    def update(self):
        self.x -= self.speed

    def rect(self):
        return pygame.Rect(int(self.x), self.y, self.breite, self.hoehe)

    def zeichne(self, surf):
        r = self.rect()
        pygame.draw.rect(surf, HINDERNIS, r, border_radius=4)
        punkte = [(r.left, r.top), (r.right, r.top), (r.centerx, r.top - 12)]
        pygame.draw.polygon(surf, (200, 50, 50), punkte)


class FliegendesHindernis:
    BREITE = 45
    HOEHE  = 22

    def __init__(self, geschwindigkeit):
        self.x     = float(BREITE + 20)
        self.y     = BODEN_Y - 55
        self.speed = geschwindigkeit

    def update(self):
        self.x -= self.speed

    def rect(self):
        return pygame.Rect(int(self.x), self.y, self.BREITE, self.HOEHE)

    def zeichne(self, surf):
        r = self.rect()
        pygame.draw.rect(surf, FLUG_F, r, border_radius=6)
        pygame.draw.polygon(surf, (220, 140, 30),
            [(r.left, r.centery), (r.left - 14, r.top), (r.left - 14, r.bottom)])
        pygame.draw.polygon(surf, (220, 140, 30),
            [(r.right, r.centery), (r.right + 14, r.top), (r.right + 14, r.bottom)])


class Wolke:
    def __init__(self):
        self.x = float(random.randint(BREITE, BREITE + 300))
        self.y = random.randint(40, 180)
        self.speed = random.uniform(0.5, 1.2)
        self.breite = random.randint(80, 160)

    def update(self):
        self.x -= self.speed

    def zeichne(self, surf):
        cx, cy = int(self.x), self.y
        b = self.breite
        pygame.draw.ellipse(surf, WOLKE_F, (cx, cy, b, 28))
        pygame.draw.ellipse(surf, WOLKE_F, (cx + b//4, cy - 14, b//2, 28))


# ──────────────────────────────────────────
# Hintergrund
# ──────────────────────────────────────────

def zeichne_hintergrund(surf, boden_offset):
    surf.fill(HIMMEL)
    random.seed(42)
    for _ in range(60):
        sx = random.randint(0, BREITE)
        sy = random.randint(0, BODEN_Y - 20)
        pygame.draw.circle(surf, (180, 180, 220), (sx, sy), 1)
    random.seed()

    boden_rect = pygame.Rect(0, BODEN_Y, BREITE, HOEHE - BODEN_Y)
    pygame.draw.rect(surf, BODEN_F, boden_rect)
    for i in range(10):
        lx = ((i * 100) - boden_offset % 100)
        pygame.draw.line(surf, (70, 70, 100), (lx, BODEN_Y), (lx, HOEHE), 1)
    pygame.draw.line(surf, (100, 100, 150), (0, BODEN_Y), (BREITE, BODEN_Y), 2)


def zeige_text_zentriert(surf, text, font, farbe, y):
    bild = font.render(text, True, farbe)
    surf.blit(bild, (BREITE // 2 - bild.get_width() // 2, y))


# ──────────────────────────────────────────
# Hauptschleife
# ──────────────────────────────────────────

def spiel():
    spieler     = Spieler()
    hindernisse = []
    plattformen = []
    wolken      = [Wolke() for _ in range(4)]

    punkte        = 0
    geschwindigkeit = 5.0
    boden_offset  = 0.0
    naechstes_hindernis = random.randint(60, 120)
    frame         = 0
    laufend       = True
    game_over     = False

    while laufend:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if game_over:
                        return spiel()
                    spieler.springe()

        if not game_over:
            frame += 1
            punkte = frame // 10
            geschwindigkeit = 5.0 + punkte * 0.01

            tasten = pygame.key.get_pressed()
            spieler.update(tasten[pygame.K_DOWN], plattformen)

            boden_offset += geschwindigkeit

            for w in wolken:
                w.update()
            wolken = [w for w in wolken if w.x > -200]
            if random.random() < 0.005:
                wolken.append(Wolke())

            # Plattformen
            if random.random() < 0.008:
                plattformen.append(Plattform(geschwindigkeit))

            for p in plattformen:
                p.speed = geschwindigkeit
                p.update()
            plattformen = [p for p in plattformen if p.x > -300]

            # Hindernisse
            naechstes_hindernis -= 1
            if naechstes_hindernis <= 0:
                if random.random() < 0.3:
                    hindernisse.append(FliegendesHindernis(geschwindigkeit))
                else:
                    if plattformen and random.random() < 0.25:
                        p = random.choice(plattformen)
                        hindernisse.append(Hindernis(geschwindigkeit, p))
                    else:
                        hindernisse.append(Hindernis(geschwindigkeit))
                naechstes_hindernis = random.randint(50, 110)

            for h in hindernisse:
                h.speed = geschwindigkeit
                h.update()
            hindernisse = [h for h in hindernisse if h.x > -60]

            # Kollision
            sp_rect = spieler.rect().inflate(-8, -8)
            for h in hindernisse:
                if sp_rect.colliderect(h.rect()):
                    game_over = True

        # Zeichnen
        zeichne_hintergrund(screen, boden_offset)

        for w in wolken:
            w.zeichne(screen)
        for p in plattformen:
            p.zeichne(screen)
        for h in hindernisse:
            h.zeichne(screen)
        spieler.zeichne(screen)

        punkte_text = font.render(f"Punkte: {punkte}", True, WEISS)
        screen.blit(punkte_text, (20, 16))

        hint = font.render("↑/Leertaste: Sprung (2x)   ↓: Ducken", True, (100, 100, 140))
        screen.blit(hint, (BREITE - hint.get_width() - 16, 16))

        if game_over:
            overlay = pygame.Surface((BREITE, HOEHE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            zeige_text_zentriert(screen, "GAME OVER", font_gross, HINDERNIS, 130)
            zeige_text_zentriert(screen, f"Punkte: {punkte}", font, WEISS, 200)
            zeige_text_zentriert(screen, "Leertaste / ↑  =  Neu starten", font, GELB, 260)

        pygame.display.flip()


if __name__ == "__main__":
    spiel()
