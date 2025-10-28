import pygame as pg
import math, os, random

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
MAX_PULL = 120


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

class StageClear:
    """ステージクリア後の画面を管理するクラス"""
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.bg = pg.Surface((1100, 650))
        self.bg.set_alpha(230)
        self.bg.fill((0, 0, 0))
        self.sc_font = pg.font.Font(None, 90)
        self.btn_font = pg.font.Font(None, 70)

        # ボタン領域
        self.next_rect = pg.Rect(330, 200, 300, 80)
        self.end_rect = pg.Rect(330, 340, 300, 80)

    def draw(self):
        """画面の描画"""
        # 背景
        self.screen.blit(self.bg, (0, 0))

        # タイトル
        sc_txt = self.sc_font.render("Stage Clear!", True, (0, 255, 0))
        self.screen.blit(sc_txt, (300, 50))

        # Nextボタン
        pg.draw.rect(self.screen, (255, 0, 0), self.next_rect)
        next_txt = self.btn_font.render("Next Stage", True, (255, 255, 255))
        self.screen.blit(next_txt, (self.next_rect.x + 30, self.next_rect.y + 20))

        # Endボタン
        pg.draw.rect(self.screen, (100, 100, 100), self.end_rect)
        end_txt = self.btn_font.render("End", True, (255, 255, 255))
        self.screen.blit(end_txt, (self.end_rect.x + 100, self.end_rect.y + 20))

        pg.display.update()

    def click(self, event):
        """クリックイベントの処理"""
        if event.type == pg.MOUSEBUTTONDOWN:
            mx, my = pg.mouse.get_pos()
            if self.next_rect.collidepoint(mx, my):
                return "next"
            elif self.end_rect.collidepoint(mx, my):
                return "end"
        elif event.type == pg.QUIT:
            return "end"
        return None

    def sentaku(self):
        """画面ループ：ユーザーの選択を待つ"""
        clock = pg.time.Clock()
        while True:
            self.draw()
            for event in pg.event.get():
                result = self.click(event)
                if result:
                    return result
            clock.tick(30)


# === 初期設定 ===
def reset_game():
    birds = [Bird((150, GROUND_Y - 40))]
    enemys = [Enemy((random.randint(450,850), GROUND_Y - random.randint(0,300))), Enemy((random.randint(450,850), GROUND_Y - random.randint(0,300)))]
    return birds, enemys

birds, enemys = reset_game()
sling_pos = (150, GROUND_Y - 40)
dragging = False
score = 0
stage = 0

# === メインループ ===
running = True
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

    # 鳥の更新と描画
    for bird in birds:
        bird.update()
        bird.draw(screen)

    # 敵の処理
    for enemy in enemys:
        if enemy.alive:
            enemy.draw(screen)
            for bird in birds:
                if bird.launched and enemy.rect.colliderect(bird.rect):
                    enemy.alive = False
                    score += 100
                    enemys.remove(enemy)
    if enemys == []:
        stageclear = StageClear(screen)
        sentaku = stageclear.sentaku()
        if sentaku == "next":
            stage += 1
            birds, enemys = reset_game()  # reset_game(stage)
        elif sentaku == "end":
            running = False
                        

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