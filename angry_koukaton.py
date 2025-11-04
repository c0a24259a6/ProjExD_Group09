import pygame as pg
import math, os
import random

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

class Life:
    """
    投げられる回数（ライフ）を管理するクラス
    """
    def __init__(self, count):
        self.max = count
        self.count = count

    def use(self):
        """
        1回分消費（戻り値: True=消費成功, False=残りなし）
        """
        if self.count > 0:
            self.count -= 1
            return True
        return False

    def can_throw(self):
        return self.count > 0

    def reset(self):
        self.count = self.max


# === 初期設定 ===
def reset_game():
    birds = [Bird((150, GROUND_Y - 40))]
    enemys = [Enemy((random.randint(450,850), GROUND_Y - random.randint(0,300))), Enemy((random.randint(450,850), GROUND_Y - random.randint(0,300))),Enemy((random.randint(450,850), GROUND_Y - random.randint(0,300)))]
    return birds, enemys

birds, enemys = reset_game()
sling_pos = (150, GROUND_Y - 40)
dragging = False
score = 0
life = Life(4)

# === メインループ ===
running = True
while running:
    screen.blit(background, (0, 0))
    screen.blit(background_tei, (0, GROUND_Y, WIDTH, 60))  # 地面

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.MOUSEBUTTONDOWN:
            # クリック時の挙動:
            # - 現在の鳥がまだ発射前ならドラッグ開始
            # - 既に発射済みで停止しておりライフが残っていれば新しい鳥をセットしてドラッグ開始（前の鳥は削除）
            if birds:
                current = birds[0]
                if not current.launched:
                    dragging = True
                else:
                    # 発射済みの鳥が "停止" していれば次の鳥をセット可能
                    if not current.active and life.can_throw():
                        # 前の鳥を取り除き、新しい鳥をスリング位置にセットしてライフを消費
                        birds.pop(0)
                        life.use()
                        birds.append(Bird(sling_pos))
                        dragging = True
            else:
                # birds が空（念のため）でライフがあれば新しい鳥をセット
                if life.can_throw():
                    life.use()
                    birds.append(Bird(sling_pos))
                    dragging = True

        elif event.type == pg.MOUSEBUTTONUP:
            if dragging and birds:
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
                life.reset()

    # 鳥の更新と描画
    for bird in list(birds):  # コピーしてループ（将来削除される可能性があるため）
        bird.update()
        bird.draw(screen)
        # 画面外に完全に出たら削除（念のため）
        if bird.pos[0] < -100 or bird.pos[0] > WIDTH + 100 or bird.pos[1] > HEIGHT + 200:
            if bird in birds:
                birds.remove(bird)

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
    else:
        # 発射前の鳥が存在するならスリング上に表示（投げていない鳥）
        if birds and not birds[0].launched:
            screen.blit(bird_img, bird_img.get_rect(center=sling_pos))

    pg.draw.circle(screen, BLACK, sling_pos, 5)

    # スコアとライフ表示
    font = pg.font.SysFont("meiryo", 24)
    text = font.render(f"Score: {score}  (R: Reset)", True, BLACK)
    screen.blit(text, (20, 20))
    life_text = font.render(f"Remaining throws: {life.count}", True, BLACK)
    screen.blit(life_text, (20, 50))

    # ゲームオーバー判定 
    if life.count == 0 and any(enemy.alive for enemy in enemys):
        font_big = pg.font.SysFont("meiryo", 60, bold=True)
        game_over_text = font_big.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//2 - 30))
        pg.display.flip()
        pg.time.wait(2000)  # 2秒表示
        running = False

    pg.display.flip()
    clock.tick(60)

pg.quit()