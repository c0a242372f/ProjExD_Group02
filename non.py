import pygame
import random
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 1. 設定とクラス定義 ---

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 100, 100)

class Unit:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_power = attack
        self.defense_power = defense

    def is_alive(self):
        """生きているかどうかの判定"""
        return self.hp > 0

    def attack(self, target):
        """targetに対して攻撃し、ダメージ計算結果とメッセージを返す"""
        
        # ダメージ計算式： (自分の攻撃力 - 相手の防御力) + 乱数(-3〜+3)
        base_damage = self.attack_power - target.defense_power
        variance = random.randint(-3, 3) 
        damage = base_damage + variance

        # ダメージは最低でも1入るようにする（0やマイナスを防ぐ）
        if damage < 1:
            damage = 1

        # 相手のHPを減らす
        target.hp -= damage
        if target.hp < 0:
            target.hp = 0

        # ログ用のメッセージを作成して返す
        return f"{self.name}の攻撃！ {target.name}に {damage} のダメージ！"
    
class BattleSprite:
    """
    戦闘キャラクターの描画
    """
    def __init__(self, image_path, x, y, size=(100, 100)):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.x = x
        self.y = y
        self.base_x = x
        self.base_y = y
        self.visible = False  # ← 最初は表示しない

        self.shake_timer = 0
        self.shake_power = 8 #  揺れの大きさ

    def show(self):
        self.visible = True

    def hit(self):
        """
        被弾時
        """
        self.shake_timer = 40 #  揺れるフレーム数

    def update(self):
        if self.shake_timer > 0:
            offset = random.randint(-self.shake_power, self.shake_power)
            self.x = self.base_x + offset
            self.shake_timer -= 1
        else:
            self.x = self.base_x

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))

class AttackEffect:
    """
    攻撃エフェクトの描画
    """
    def __init__(self, image_path, x, y, size=(50, 50)):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.x = x
        self.y = y
        self.timer = 0
        self.visible = False

    def play(self):
        self.timer = 40   # 表示フレーム数
        self.visible = True

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.visible = False

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))



# --- 2. Pygame初期化 ---
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("RPG")

# 日本語フォントの設定（環境に合わせてフォントを探します）
font_name = pygame.font.match_font('meiryo', 'yu gothic', 'hiragino maru gothic pro')
font = pygame.font.Font(font_name, 24)
 
# --- 3. ゲームデータの準備 ---
hero = Unit(name="勇者", hp=100, attack=30, defense=10)
demon = Unit(name="魔王", hp=250, attack=25, defense=5)
demon_sprite = BattleSprite("images/go-remu.png", 400, 120)  # 敵のインスタンス生成
hero_sprite = BattleSprite("images/hero.png", 50, 120)  # 勇者のインスタンス生成
slash_effect = AttackEffect("images/slash.png", 380, 180)  # 勇者の攻撃エフェクトのインスタンス生成
slash2_effect = AttackEffect("images/slash2.png", 130, 180)  # 敵の攻撃エフェクトのインスタンス生成

# 戦闘ログ（画面に表示するテキストのリスト）
battle_logs = ["スペースキーを押してバトル開始！"]

turn = "PLAYER" # どちらのターンか
game_over = False

# --- 4. メインループ ---
running = True
while running:
    screen.fill(BLACK) # 画面をリセット

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            # ウィンドウの閉じるボタンが押されたらループを抜ける
            break
        
        # スペースキーが押されたらターンを進める
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            hero_sprite.show()  # 勇者の呼び出し
            demon_sprite.show()  # 敵の呼び出し
            if not game_over:
                if turn == "PLAYER":
                    # 勇者の攻撃処理
                    msg = hero.attack(demon)
                    demon_sprite.hit()  # 敵が揺れる
                    slash_effect.play()  # 勇者の攻撃エフェクト
                    battle_logs.append(msg) # ログに追加
                    
                    if not demon.is_alive():
                        battle_logs.append("魔王を倒した！")
                        game_over = True
                    else:
                        turn = "ENEMY" # 相手のターンへ
                
                elif turn == "ENEMY":
                    # 魔王の攻撃処理
                    msg = demon.attack(hero)
                    hero_sprite.hit()  # 勇者が揺れる
                    slash2_effect.play()  # 敵の攻撃エフェクト
                    battle_logs.append(msg)
                    
                    if not hero.is_alive():
                        battle_logs.append("勇者は力尽きた...")
                        game_over = True
                    else:
                        turn = "PLAYER" # プレイヤーのターンへ
            else:
                # ゲームオーバー後
                battle_logs.append("ゲーム終了。閉じるボタンで終了してください。")

    # --- 描画処理 ---

    
    # 1. ステータス表示（画面上部）
    hero_text = font.render(f"{hero.name} HP: {hero.hp}/{hero.max_hp}", True, WHITE)
    demon_text = font.render(f"{demon.name} HP: {demon.hp}/{demon.max_hp}", True, RED)
    screen.blit(hero_text, (50, 50))
    screen.blit(demon_text, (400, 50))

    # 2. ログの表示（最新の5行だけ表示する）
    # リストの後ろから5つを取得して表示
    recent_logs = battle_logs[-5:] 

    # 3. キャラの表示
    hero_sprite.update()
    demon_sprite.update()
    hero_sprite.draw(screen)
    demon_sprite.draw(screen)
    slash_effect.update()
    slash_effect.draw(screen)
    slash2_effect.update()
    slash2_effect.draw(screen)
    
    y = 150 # テキストを表示し始めるY座標
    for log in recent_logs:
        text_surface = font.render(log, True, WHITE)
        screen.blit(text_surface, (50, y))
        y += 40 # 行間をあける

    # 3. 操作ガイド
    if not game_over:
        guide_text = font.render("[SPACE]でターンを進める", True, (100, 255, 100))
        screen.blit(guide_text, (200, 400))

    pygame.display.flip()

pygame.quit()
sys.exit()