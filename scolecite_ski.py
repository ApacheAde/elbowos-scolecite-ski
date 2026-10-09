#!/usr/bin/env python3
"""Scolecite Ski — neon needle-slope arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/SCOLECITE_SKI_ElbowOS.mp4")
TITLE, HANDLE = "SCOLECITE SKI", "x.com/ElbowOS"
DUSK = (18, 8, 36)
TEAL = (64, 255, 214)
FROST = (236, 246, 255)
COPPER = (255, 148, 72)
MAG = (255, 78, 168)
INK = (8, 4, 18)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont("dejavusans", 72, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 34, bold=True)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 1
        self.x = W * 0.5
        self.vx = 0
        self.y = 680
        self.vy = 0
        self.ground = 0
        self.scroll = 6.4
        self.cam = 0.0
        self.spawn = 400
        self.obs = []
        self.pops = []
        self.snow = [[random.randrange(W), random.randrange(H), random.uniform(1, 3.4)] for _ in range(90)]
        self.trail = []
        self.keys = {"l": False, "r": False, "j": False}
        for _ in range(8):
            self._spawn(ahead=True)

    def _spawn(self, ahead=False):
        kind = random.choice(["spike", "spike", "gem", "gate", "gap"])
        x = random.randint(140, W - 140)
        y = self.cam + (random.randint(220, 520) if ahead else H + random.randint(40, 280))
        self.obs.append({"k": kind, "x": x, "y": y, "hit": False, "w": random.randint(70, 150)})
        self.spawn = y

    def step(self):
        self.t += 1
        self.scroll = min(16.5, 6.2 + self.t * 0.012)
        self.cam += self.scroll
        lean = (-1 if self.keys["l"] else 0) + (1 if self.keys["r"] else 0)
        self.vx += lean * 1.35
        self.vx *= 0.86
        self.x = max(90, min(W - 90, self.x + self.vx))
        if self.keys["j"] and self.ground <= 0:
            self.vy = -16
            self.ground = 1
        if self.ground > 0:
            self.vy += 0.85
            self.y += self.vy
            if self.y >= 680:
                self.y, self.vy, self.ground = 680, 0, 0
        self.trail.append((self.x, self.y + 28))
        self.trail = self.trail[-18:]
        while self.spawn < self.cam + H + 200:
            self._spawn()
        keep = []
        for o in self.obs:
            if o["y"] < self.cam - 80:
                continue
            keep.append(o)
            if o["hit"]:
                continue
            sy = o["y"] - self.cam
            if abs(sy - self.y) < 46 and abs(o["x"] - self.x) < (70 if o["k"] != "gate" else 36):
                if o["k"] == "gem":
                    self.score += 25 * self.combo
                    self.combo = min(9, self.combo + 1)
                    self.pops.append([o["x"], sy, 18, "+%d" % (25 * (self.combo - 1) or 25)])
                    o["hit"] = True
                elif o["k"] == "gate":
                    self.score += 40
                    self.pops.append([o["x"], sy, 16, "THREAD"])
                    o["hit"] = True
                elif o["k"] == "gap" and self.ground == 0:
                    self.score = max(0, self.score - 15)
                    self.combo = 1
                    self.pops.append([o["x"], sy, 14, "CREVASSE"])
                    o["hit"] = True
                elif o["k"] == "spike" and self.ground == 0:
                    self.combo = 1
                    self.vx = 18 if self.x < o["x"] else -18
                    self.pops.append([self.x, self.y, 12, "NEEDLE"])
                    o["hit"] = True
                elif o["k"] in ("spike", "gap") and self.ground > 0:
                    self.score += 10
                    o["hit"] = True
                    self.pops.append([self.x, self.y - 20, 12, "OLLIE"])
        self.obs = keep
        for s in self.snow:
            s[1] += s[2] * 3.2 + self.scroll * 0.35
            s[0] += math.sin(self.t * 0.05 + s[2]) * 0.6
            if s[1] > H:
                s[1] = -8
                s[0] = random.randrange(W)
        self.pops = [[p[0], p[1] - 2, p[2] - 1, p[3]] for p in self.pops if p[2] > 0]

    def auto(self):
        look = [o for o in self.obs if 40 < (o["y"] - self.cam - self.y) < 420 and not o["hit"]]
        target = self.x
        danger = None
        gem = None
        for o in look:
            if o["k"] in ("spike", "gap") and abs(o["x"] - self.x) < 160:
                if danger is None or o["y"] < danger["y"]:
                    danger = o
            if o["k"] == "gem" and (gem is None or o["y"] < gem["y"]):
                gem = o
            if o["k"] == "gate" and (gem is None or o["y"] < gem["y"]):
                gem = o
        if danger:
            target = danger["x"] + (220 if self.x >= danger["x"] else -220)
        elif gem:
            target = gem["x"]
        self.keys["l"] = self.x > target + 18
        self.keys["r"] = self.x < target - 18
        near = danger and (danger["y"] - self.cam - self.y) < 150 and abs(danger["x"] - self.x) < 90
        self.keys["j"] = bool(near and self.ground <= 0 and self.t % 7 == 0)

    def draw(self, surf):
        surf.fill(INK)
        for i in range(H):
            u = i / H
            col = (int(18 + 40 * u), int(8 + 28 * (1 - u)), int(36 + 70 * (1 - u * 0.4)))
            pygame.draw.line(surf, col, (0, i), (W, i))
        origin = (W // 2, int(220 - (self.cam * 0.15) % 80))
        for i in range(18):
            ang = -0.9 + i * 0.1 + math.sin(self.t * 0.02 + i) * 0.02
            x2 = origin[0] + math.sin(ang) * 1400
            y2 = origin[1] + math.cos(ang) * 1700
            pygame.draw.line(surf, (70, 90, 130), origin, (x2, y2), 2)
        pygame.draw.polygon(surf, (28, 16, 52), [(0, 980), (180, 760), (0, 1500)])
        pygame.draw.polygon(surf, (32, 18, 58), [(W, 900), (W - 200, 700), (W, 1460)])
        for o in self.obs:
            sy = int(o["y"] - self.cam)
            if sy < -80 or sy > H + 40:
                continue
            if o["k"] == "spike":
                pts = [(o["x"], sy - 70), (o["x"] - 46, sy + 36), (o["x"] + 46, sy + 36)]
                pygame.draw.polygon(surf, FROST if not o["hit"] else (90, 100, 120), pts)
                pygame.draw.polygon(surf, TEAL, pts, 3)
            elif o["k"] == "gem":
                c = COPPER if not o["hit"] else (80, 60, 40)
                pygame.draw.circle(surf, c, (int(o["x"]), sy), 22)
                pygame.draw.circle(surf, FROST, (int(o["x"]) - 6, sy - 6), 6)
            elif o["k"] == "gate":
                col = MAG if not o["hit"] else (90, 40, 70)
                pygame.draw.rect(surf, col, (o["x"] - 70, sy - 80, 16, 120), border_radius=6)
                pygame.draw.rect(surf, col, (o["x"] + 54, sy - 80, 16, 120), border_radius=6)
                pygame.draw.arc(surf, TEAL, (o["x"] - 70, sy - 110, 140, 70), 0, math.pi, 4)
            else:
                pygame.draw.rect(surf, (12, 6, 22), (o["x"] - 80, sy - 10, 160, 36))
                pygame.draw.line(surf, COPPER, (o["x"] - 80, sy - 10), (o["x"] + 80, sy - 10), 3)
        for i, (tx, ty) in enumerate(self.trail):
            pygame.draw.circle(surf, (40, 180, 160), (int(tx), int(ty)), max(2, i // 3))
        bob = math.sin(self.t * 0.4) * 3
        rx, ry = int(self.x), int(self.y + bob)
        pygame.draw.line(surf, TEAL, (rx - 36, ry + 34), (rx + 28, ry + 22), 7)
        pygame.draw.circle(surf, (255, 214, 120), (rx, ry - 8), 18)
        pygame.draw.polygon(surf, TEAL, [(rx - 16, ry + 6), (rx + 18, ry + 4), (rx, ry + 36)])
        pygame.draw.circle(surf, FROST, (rx + 6, ry - 14), 5)
        for s in self.snow:
            pygame.draw.circle(surf, (210, 230, 255), (int(s[0]), int(s[1])), int(s[2]))
        for p in self.pops:
            lab = self.small.render(p[3], True, COPPER)
            surf.blit(lab, lab.get_rect(center=(int(p[0]), int(p[1]))))
        banner = pygame.Surface((W, 150), pygame.SRCALPHA)
        banner.fill((8, 4, 18, 170))
        surf.blit(banner, (0, 0))
        surf.blit(self.font.render(TITLE, True, TEAL), (36, 28))
        sc = self.mid.render("SCORE  %05d   x%d" % (self.score, self.combo), True, FROST)
        surf.blit(sc, (36, 104))
        foot = pygame.Surface((W, 90), pygame.SRCALPHA)
        foot.fill((8, 4, 18, 180))
        surf.blit(foot, (0, H - 90))
        h = self.mid.render(HANDLE, True, MAG)
        surf.blit(h, h.get_rect(center=(W // 2, H - 46)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_a, pygame.K_LEFT):
                        self.keys["l"] = True
                    if ev.key in (pygame.K_d, pygame.K_RIGHT):
                        self.keys["r"] = True
                    if ev.key in (pygame.K_SPACE, pygame.K_w):
                        self.keys["j"] = True
                    if ev.key == pygame.K_r:
                        self.reset()
                if ev.type == pygame.KEYUP:
                    if ev.key in (pygame.K_a, pygame.K_LEFT):
                        self.keys["l"] = False
                    if ev.key in (pygame.K_d, pygame.K_RIGHT):
                        self.keys["r"] = False
                    if ev.key in (pygame.K_SPACE, pygame.K_w):
                        self.keys["j"] = False
            self.step()
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        n = FPS * SECS
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "20", "-movflags", "+faststart", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(n):
                self.auto()
                self.step()
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tostring(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit("ffmpeg failed (%s): %s" % (rc, err[-1200:]))
        print("wrote", OUT)

def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()
        pygame.quit()

if __name__ == "__main__":
    main()
