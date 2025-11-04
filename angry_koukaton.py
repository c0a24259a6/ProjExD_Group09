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
# === Shieldクラスの追加 ===
class Shield:
    def __init__(self, pos, width, height):
        
        # Shieldオブジェクトの初期化
        # pos:    矩形の左上の座標 (x, y)
        # width:  矩形の幅
        # height: 矩形の高さ
        
        # 位置と大きさを持つ四角形(Rect)オブジェクトを作成
        self.rect = pg.Rect(pos[0], pos[1], width, height)
        # 壁の色をBLACKに設定
        self.color = BLACK
        # 壁が存在しているかどうかのフラグ（Trueなら表示、Falseなら非表示）
        self.alive = True

    def draw(self, surf):
        # self.alive が True の場合のみ壁を描画する
        if self.alive:
            pg.draw.rect(surf, self.color, self.rect)

# === 初期設定 ===
def reset_game():
    birds = [Bird((150, GROUND_Y - 40))]
    enemys = [Enemy((650, GROUND_Y - 40)), Enemy((750, GROUND_Y - 100))]
    # Shieldの幅と高さを定義
    shields = []  # まず、空のリストを用意
    shield_count = 2  # 生成したい壁の数を設定
    shield_start_x = 600  # 1つ目の壁のx座標
    shield_interval = 100 # 壁と壁の間隔
    shield_width = 20  # 幅を20に設定
    shield_height = bird_img.get_rect().height * 4  # 高さを鳥の画像の2倍に設定

    for i in range(shield_count):
        x = shield_start_x + i * shield_interval # shield_countの数だけ壁を生成
        y = GROUND_Y - shield_height
        shields.append(Shield((x, y), shield_width, shield_height)) # shieldsリストに追加
    return birds, enemys, shields


birds, enemys, shields = reset_game()
sling_pos = (150, GROUND_Y - 40)
dragging = False
score = 0

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
                birds, enemys, shields= reset_game()
                score = 0

    # 鳥の更新と描画
    for bird in birds:
        bird.update()
        bird.draw(screen)
     # 盾の処理と描画
    for shield in shields:
        shield.draw(screen) # 盾を描画
        for bird in birds:
            # 鳥と盾の衝突判定
            # 条件：鳥が発射済み(launched) AND 盾が存在(alive) AND 鳥と盾の矩形が衝突しているか
            if bird.launched and shield.alive and shield.rect.colliderect(bird.rect):
                bird.vel[0] = -1.0 # 鳥のX方向(横)の速度を反転させて跳ね返らせる

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