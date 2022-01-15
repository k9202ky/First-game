import pygame
import random
import os

FPS = 60
WIDTH = 1000
HEIGHT = 1000

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
#遊戲初始化 創建視窗
pygame.init() 
pygame.mixer.init() 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("M14打歌利亞")
clock = pygame.time.Clock()

#載入圖片
background_img = pygame.image.load(os.path.join("img", "background.jpg")).convert()
shield_img = pygame.image.load(os.path.join("img", "shield.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert() 
player_mini_img = pygame.transform.scale(player_img, (100, 95))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
obstacle_imgs = []
for i in range(2):
    obstacle_imgs.append(pygame.image.load(os.path.join("img", f"obstacle{i}.png")).convert())
expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (283, 211)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (100, 100)))
    player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(pygame.transform.scale(player_expl_img, (283, 211)))

#載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.mp3"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "M14_BREAK_JP.wav"))
expl_sound = pygame.mixer.Sound(os.path.join("sound", "expl.mp3"))
Go_attack_sound = pygame.mixer.Sound(os.path.join("sound", "M14_GOATTACK_JP.wav"))
injure_sound = pygame.mixer.Sound(os.path.join("sound", "M14_SKILL2_JP.wav"))
respawn_sound = pygame.mixer.Sound(os.path.join("sound", "M14_PHRASE_JP.wav"))
get_shield_sound = pygame.mixer.Sound(os.path.join("sound", "M14_FEED_JP.wav"))
pygame.mixer.music.load(os.path.join("sound", "Xomu - Lanterns.mp3"))
pygame.mixer.music.set_volume(0.5)

#引入字體
font_name = os.path.join("font.ttf")
def draw_txt_w(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    #True是反鋸齒 
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def draw_txt_r(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    #True是反鋸齒 
    text_surface = font.render(text, True, RED)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def new_obstacle():
    o = Obstacle()
    all_sprites.add(o)
    obstacles.add(o)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 150
    BAR_HEIGHT = 10
    fill = (hp/100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    #第4個參數是外框的像素，要是不加的話外框會被填滿
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 100 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(pygame.transform.scale(background_img, (1000, 1000)), (0, 0))
    draw_txt_r(screen, 'M14打歌利亞', 100, WIDTH/2, HEIGHT/4)
    draw_txt_r(screen, '方向鍵 and WASD 移動人物 空白鍵發射子彈', 50, WIDTH/2, HEIGHT/2)
    draw_txt_r(screen, '按任意鍵開始遊戲', 25, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP : 
                waiting = False 
                return False

#製作成員
class Player(pygame.sprite.Sprite):
    def __init__(self) :
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (200, 190))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = self.rect.width *0.8 / 2
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT -15
        self.speed = 7
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_time > 7000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 15
        
        if  self.hidden and pygame.time.get_ticks() - self.hide_time > 8000:
            self.hidden = False
            respawn_sound.play()

        key_pressed = pygame.key.get_pressed()
        
        if key_pressed[pygame.K_UP] or key_pressed[pygame.K_w]:
            self.rect.y -= self.speed 
        if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a]:
            self.rect.x -= self.speed
        if key_pressed[pygame.K_DOWN] or key_pressed[pygame.K_s]:
            self.rect.y += self.speed
        if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]:
            self.rect.x += self.speed
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0    
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT and not(self.hidden):
            self.rect.bottom = HEIGHT
            
    def shoot(self):
        if not(self.hidden):
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
    
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        #把player移到視窗外
        self.rect.center = (WIDTH/2, HEIGHT+1000)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self) :
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(obstacle_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width *0.6 /2
        #pygame.draw.circle(self.image_ori, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-500, -100)
        self.speedy = random.randrange(5, 10)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def  rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-500, -100)
            self.speedy = random.randrange(5, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y) :
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (20,50))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()
        
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size) :
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Shield(pygame.sprite.Sprite):
    def __init__(self, center) :
        pygame.sprite.Sprite.__init__(self)
        self.image = shield_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = +5

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

#-1表示無限循環播放
pygame.mixer.music.play(-1)

#遊戲迴圈
show_init = True
running = True
lost = False
lost_count = 0
while running:
    if show_init:
        close = draw_init()
        if close:
            #如果關閉視窗就要跳出遊戲迴圈
            break
        show_init = False
        Go_attack_sound.play()
        #製作群組
        all_sprites = pygame.sprite.Group()
        obstacles = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        shields = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        #障礙物持續落下15個
        for i in range(15):
            new_obstacle()
        score = 0
        lost_count = 0

    #畫面顯示
    screen.fill(BLACK)
    screen.blit(pygame.transform.scale(background_img, (1000, 1000)), (0, 0))
    all_sprites.draw(screen)
    draw_txt_w(screen, str(score), 30, WIDTH/2, 10)
    draw_health(screen, player.health, 50, 40)
    draw_lives(screen, player.lives, player_mini_img, WIDTH * 3/4 - 55, 10) 
    if lost:
        draw_txt_w(screen, 'GG', 100, WIDTH/2, 350)
    pygame.display.update()

    #每秒執行FPS次迴圈
    clock.tick(FPS)
                           
    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  
            player.shoot() 
            
    #更新遊戲
    all_sprites.update()
    #2個布林值分別代表障礙物和子彈碰撞後是否刪除
    #圓形邊框消除判定
    #hits這個字典裡是碰撞到的obstacle跟bullet
    hits = pygame.sprite.groupcollide(obstacles, bullets, True, True, pygame.sprite.collide_circle)  
    #障礙物刪除後要加回去
    for hit in hits:
        expl_sound.play()
        score += 100   
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        #shield出現機率為1成
        if random.random() > 0.9:
            shield = Shield(hit.rect.center)
            all_sprites.add(shield)
            shields.add(shield)
        new_obstacle()

    #布林值表示player和obstacles相撞時要不要刪除，hits是所有碰撞到player的obstacle
    hits = pygame.sprite.spritecollide(player, obstacles, True, pygame.sprite.collide_circle)
    for hit in hits:
        expl_sound.play()
        new_obstacle()
        player.health -= 10
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.health == 50: 
            injure_sound.play()
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            if player.lives > 0:
                die_sound.play()
            player.lives -= 1
            player.hide()
            if player.lives > 0:
                player.health = 100

    hits = pygame.sprite.spritecollide(player, shields, True, pygame.sprite.collide_circle)           
    for hit in hits:
        player.health += 20
        get_shield_sound.play()
        if player.health > 100:
            player.health = 100      

    if player.lives == 0:
        lost = True
        lost_count += 1

    if lost:
        if lost_count > FPS * 7:
            lost = False
            show_init = True
        else:
            continue

pygame.quit()
