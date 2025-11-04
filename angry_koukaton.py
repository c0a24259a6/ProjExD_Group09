import pygame as pg
import math, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pg.init()
WIDTH, HEIGHT = 900, 500
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Image Angry Birds")
clock = pg.time.Clock()

# === 画像読み込み ===
background = pg.image.load(f"fig/sora.png")
background_tei = pg.image.load(f"fig/jimen.png")
bird_img = pg.image.load(f"fig/3.png")
enemy_img = pg.image.load(f"fig/0.png")

# サイズ調整
bird_img = pg.transform.scale(bird_img, (40, 40))
enemy_img = pg.transform.scale(enemy_img, (45, 45))
background = pg.transform.scale(background, (WIDTH, HEIGHT))

# === 定義 ===
BLACK = (0, 0, 0)
GROUND_Y = HEIGHT - 60
GRAVITY = 0.5
POWER = 0.2
MAX_PULL = 100

# === クラス ===
class Bird:
    def __init__(self, pos):
        self.pos = list(pos)
        self.vel = [0, 0]
        self.img = bird_img
        self.rect = self.img.get_rect(center=pos)
        self.launched = False
        self.active = True

    def update(self):
        if self.launched and self.active:
            self.vel[1] += GRAVITY
            self.pos[0] += self.vel[0]
            self.pos[1] += self.vel[1]
            self.rect.center = (self.pos[0], self.pos[1])

            # 地面で停止
            if self.pos[1] > GROUND_Y - self.rect.height // 2:
                self.pos[1] = GROUND_Y - self.rect.height // 2
                self.vel[1] *= -0.4
                self.vel[0] *= 0.8
                if abs(self.vel[1]) < 1 and abs(self.vel[0]) < 1:
                    self.active = False

    def draw(self, surf):
        surf.blit(self.img, self.rect)


class Enemy:
    def __init__(self, pos):
        self.pos = list(pos)
        self.img = enemy_img
        self.rect = self.img.get_rect(center=pos)
        self.alive = True

    def draw(self, surf):
        if self.alive:
            surf.blit(self.img, self.rect)


class Drop:
    def __init__(self, bird):
        self.bird = bird
        self.active = True

    def update(self):
        if self.active:
            self.bird.pos[1] += 18# 毎フレームの落下量
            if self.bird.pos[1] >= GROUND_Y - self.bird.rect.height:#こうかとんが地面についたら
                self.bird.pos[1] = GROUND_Y - self.bird.rect.height#止める
                self.active = False#落下を終わる
            self.bird.rect.center = (self.bird.pos[0], self.bird.pos[1])

# === 初期設定 ===
def reset_game():
    birds = [Bird((150, GROUND_Y - 40))]
    enemys = [Enemy((650, GROUND_Y - 40)), Enemy((750, GROUND_Y - 100))]
    return birds, enemys

birds, enemys = reset_game()
sling_pos = (150, GROUND_Y - 40)
dragging = False
score = 0

# === メインループ ===
running = True
drop=None
while running:
    screen.blit(background, (0, 0))
    screen.blit(background_tei, (0, GROUND_Y, WIDTH, 60))  # 地面

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.MOUSEBUTTONDOWN:
            if birds and not birds[0].launched:
                dragging = True

        elif event.type == pg.MOUSEBUTTONUP:
            if dragging:
                dragging = False
                mx, my = pg.mouse.get_pos()
                dx = sling_pos[0] - mx
                dy = sling_pos[1] - my
                dist = math.hypot(dx, dy)
                if dist > MAX_PULL:
                    scale = MAX_PULL / dist
                    dx *= scale
                    dy *= scale
                birds[0].vel = [dx * POWER, dy * POWER]
                birds[0].launched = True

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                birds, enemys = reset_game()
                score = 0
            elif event.key == pg.K_RETURN:  # エンターキーで落下開始
                drop = Drop(birds[0])


    # 鳥の更新と描画
    for bird in birds:
        bird.update()
        bird.draw(screen)
    #  
    if drop is not None:
        drop.update()
    

    # 敵の処理
    for enemy in enemys:
        if enemy.alive:
            enemy.draw(screen)
            for bird in birds:
                if bird.launched and enemy.rect.colliderect(bird.rect):
                    enemy.alive = False
                    score += 100

    # スリング描画
    if dragging:
        mx, my = pg.mouse.get_pos()
        pg.draw.line(screen, BLACK, sling_pos, (mx, my), 3)
        screen.blit(bird_img, bird_img.get_rect(center=(mx, my)))

    pg.draw.circle(screen, BLACK, sling_pos, 5)

    # スコア
    font = pg.font.SysFont("meiryo", 24)
    text = font.render(f"Score: {score}  (R: Reset)", True, BLACK)
    screen.blit(text, (20, 20))

    pg.display.flip()
    clock.tick(60)

pg.quit()