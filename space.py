import time
import os
import pygame
import random

pygame.init()

#Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
CYAN = (0,255,255)
GREY = (120,120,120)

#Game window
window_x = 900
window_y = 600
fps = 60
clock = pygame.time.Clock()
game_window = pygame.display.set_mode((window_x, window_y))
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load(os.path.join('Graphics', 'astronaut.png'))
pygame.display.set_icon(icon)

#Images
start_background = pygame.image.load('Graphics/start.png').convert()
gameplay_background = pygame.image.load('Graphics/gameplay.png').convert()
bom = pygame.image.load('Graphics/bom.png')
fire_bullet = pygame.image.load('Graphics/fire-bullet.png')
yellow = pygame.image.load('Graphics/yellow-alien.png')
purple = pygame.image.load('Graphics/purple-alien.png')
red = pygame.image.load('Graphics/red-alien.png')
boss = pygame.image.load('Graphics/boss.png')
star = pygame.image.load('Graphics/Star.png')
heart = pygame.image.load('Graphics/Heart.png')
shield = pygame.image.load('Graphics/Shield.png')
potion1 = pygame.image.load('Graphics/Potion1.png')
potion2 = pygame.image.load('Graphics/Potion2.png')
potion3 = pygame.image.load('Graphics/Potion3.png')

snow = pygame.image.load('Graphics/Obs1.png')
wind = pygame.image.load('Graphics/Obs2.png')
water = pygame.image.load('Graphics/Obs3.png')
tree = pygame.image.load('Graphics/Obs4.png')
fire = pygame.image.load('Graphics/Obs5.png')

#Fonts
font_30 = pygame.font.SysFont('Costantia', 32)
font_50 = pygame.font.SysFont('Costantia', 50)
font_80 = pygame.font.SysFont('Costantia', 80)
font_100 = pygame.font.SysFont('Oswald', 100)

#Texts
text = font_100.render("SPACE INVADERS", True, WHITE)
text1 = font_30.render("Press Enter to Play!", True, WHITE)
text2 = font_30.render("Press P to Pause!", True, WHITE)
text3 = font_30.render("Press C to Continue!", True, WHITE)


#Modes
start = False
running = True

#Vars
levels = 1
wave_length = 5
fire_obs = False
water_obs = False
paused = False
last_alien_shot = pygame.time.get_ticks()
score = 0
count = [0,0,0,0]

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Graphics/spaceship.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

        #Drugs
        self.shield = False
        self.potion1 = False
        self.potion2 = False
        self.potion3 = False

        #Obs
        self.snow = False
        self.wind = False

    def update(self):
        if not self.snow:
            speed = 6#per frame
        else:
            speed = 3

        if not self.potion2:
            cooldown = 600 #milisecs
        else:
            cooldown = 300
        #Mask
        self.mask = pygame.mask.from_surface(self.image)

        key = pygame.key.get_pressed()
        if not self.wind:
            if key[pygame.K_w] and self.rect.top > 0:
                self.rect.y -= speed
            if key[pygame.K_s] and self.rect.bottom + 20 < window_y:
                self.rect.y += speed
            if key[pygame.K_a] and self.rect.left > 0:
                self.rect.x -= speed
            if key[pygame.K_d] and self.rect.right < window_x:
                self.rect.x += speed
        else:
            if key[pygame.K_w] and self.rect.bottom + 20 < window_y:
                self.rect.y += speed
            if key[pygame.K_s] and self.rect.top > 0:
                self.rect.y -= speed
            if key[pygame.K_a] and self.rect.right < window_x:
                self.rect.x += speed
            if key[pygame.K_d] and self.rect.left > 0:
                self.rect.x -= speed


        #Shot cooldown
        time_now = pygame.time.get_ticks()
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = pygame.time.get_ticks()

        #Health bar
        if self.health_remaining > 0:
            for i in range(self.health_remaining):
                game_window.blit(heart, (window_x - heart.get_width()*(i+1), 5))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            self.kill()
            game_over()

        #Set affecting time and animations for drugs
        if self.shield:
            self.affecting(shield, 'shield', 0, 10)
        if self.potion1:
            self.affecting(potion1, 'potion1', 1, 10)
        if self.potion2:
            self.affecting(potion2, 'potion2', 2, 10)
        if self.potion3:
            self.affecting(potion3, 'potion3', 3, 10)

        #Collide with aliens
        if pygame.sprite.spritecollide(self, alien_group, True, pygame.sprite.collide_mask):
            self.health_remaining = 0

        #Reset obs
        if len(alien_group) == 0:
            self.snow = False
            self.wind = False

    def affecting(self, surface, drug, index, timecount):
        global count
        count[index] += 1
        if drug == 'shield':
            game_window.blit(surface, (window_x - surface.get_width(), 40))
            if count[index] == fps * timecount:
                self.shield = False
                count[index] = 0
        elif drug == 'potion1':
            game_window.blit(surface, (window_x - surface.get_width() - 32, 40))
            if count[index] == fps * timecount:
                self.potion1 = False
                count[index] = 0
        elif drug == 'potion2':
            game_window.blit(surface, (window_x - surface.get_width() - 58 , 40))
            if count[index] == fps * timecount:
                self.potion2 = False
                count[index] = 0
        elif drug == 'potion3':
            game_window.blit(surface, (window_x - surface.get_width() - 82 , 40))
            if count[index] == fps * timecount:
                self.potion3 = False
                count[index] = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Graphics/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        if not spaceship.potion1:
            self.rect.y -= 5
        else:
            self.rect.y -= 10     
        if self.rect.bottom < 0:
            self.kill()


class Alien(pygame.sprite.Sprite):
    TYPE_MAP = {
        'red': ('red', red, 10, random.choice([-1, 1]), 2),
        'yellow': ('yellow', yellow, 10, random.choice([-2, 2]), 1),
        'purple': ('purple', purple, 10, random.choice([-1, 1]), 1),
        'boss': ('boss', boss, 10, random.choice([-1, 1]), 0)
    }
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.cate, self.image, self.health, self.Xvel, self.Yvel = self.TYPE_MAP[random.choice(['red', 'yellow', 'purple', 'boss'])]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_remaining = self.health

    def update(self):
        #Mask
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x += self.Xvel
        self.rect.y += self.Yvel
        if self.rect.left < 0 or self.rect.right > window_x:
            self.Xvel = -self.Xvel
        if self.rect.top < 0 or self.rect.bottom > 200:
            self.Yvel = -self.Yvel
        if self.rect.top > window_y:
            self.kill()

        #Collision with bullets
        if pygame.sprite.spritecollide(self, bullet_group, True, pygame.sprite.collide_mask):
            global score
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            if spaceship.potion3 == True:
                self.health_remaining -= 20
            else:
                self.health_remaining -= 10
        if self.health_remaining <= 0:
            self.kill()
            score += self.health
            rate = random.randrange(1,3)
            if rate == 2:
                bonus = Bonus(self.rect.centerx, self.rect.centery)
                bonus_group.add(bonus)


class Alien_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        img = image
        self.image = pygame.transform.scale(img, (23,32))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 5
        if self.rect.top > window_y:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
            if not spaceship.shield:
                spaceship.health_remaining -= 1
            else:
                pass


class Bonus(pygame.sprite.Sprite):
    TYPE_MAP = {
        'heart': (heart, 'heart'),
        'potion1': (potion1, 'potion1'), #Increases bullet's speed by 50%
        'potion2': (potion2, 'potion2'), #Increases bullet's speed by 50%
        'potion3': (potion3, 'potion3'), #Increases bullet's speed by 50%
        'shield': (shield, 'shield')
    }
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.cate = self.TYPE_MAP[random.choice(['heart', 'potion1', 'potion2', 'potion3', 'shield'])]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        global count

        self.mask = pygame.mask.from_surface(self.image)
        self.rect.y += 1

        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            if self.cate == 'heart':
                if spaceship.health_remaining < 3:
                    spaceship.health_remaining += 1
            if self.cate == 'shield':
                if not spaceship.shield:
                    spaceship.shield = True
                else:
                    count[0] = 0
            if self.cate == 'potion1':
                if not spaceship.potion1:
                    spaceship.potion1 = True
                else:
                    count[1] = 0
            if self.cate == 'potion2':
                if not spaceship.potion2:
                    spaceship.potion2 = True
                else:
                    count[2] = 0
            if self.cate == 'potion3':
                if not spaceship.potion3:
                    spaceship.potion3 = True
                else:
                    count[3] = 0


class Obstacle(pygame.sprite.Sprite):
    TYPE_MAP = {
        'fire': (fire, 'fire'), #Random fire-balls pouring down
        'water': (water, 'water'), #Lower alien's bullets cooldown
        'wind': (wind, 'wind'), #Redirect the movement - Move in opposite direction
        'snow': (snow, 'snow') #Slowing down the space ship
    }
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.cate = self.TYPE_MAP[random.choice(['fire', 'water', 'wind', 'snow'])]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        global fire_obs, water_obs

        if len(alien_group) == 0:
            self.kill()
        if self.cate == 'wind':
            spaceship.wind = True
        if self.cate == 'snow':
            spaceship.snow = True
        if self.cate == 'fire':
            fire_obs = True
        if self.cate == 'water':
            water_obs = True


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'Graphics/exp{num}.png')
            if size == 1:
                img = pygame.transform.scale(img, (30,30))
            if size == 2:
                img = pygame.transform.scale(img, (60,60))
            if size == 3:
                img = pygame.transform.scale(img, (120,120))
            #Add images to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        explosion_threshold = 3

        self.counter += 1
        if self.counter >= explosion_threshold and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        if self.counter >= explosion_threshold and self.index >= len(self.images) - 1:
            self.kill()

    
#Sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
fire_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
bonus_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()

#Create player (spaceship)
spaceship = Spaceship(window_x/2, window_y - 80, 3)
spaceship_group.add(spaceship)

def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    game_window.blit(surface, (x,y))

def create_aliens():
    for i in range(wave_length+levels):
        alien = Alien(random.randint(64, window_x-64), random.randint(32, 64))
        alien_group.add(alien)

def create_obs():
    for i in range(2):
        obs = Obstacle(32*i + 16, 16)
        obstacle_group.add(obs)

def show_score():
    score_surface = font_50.render(str(score).upper(), True, WHITE)
    game_window.blit(score_surface, (window_x/2 - (score_surface.get_width() - 10)/2, 5))

def game_over():
    game_over_surface = font_100.render("Your score is : "+str(score), True, (255,255,255))
    game_window.blit(game_over_surface, (window_x/2 - (game_over_surface.get_width()-10)/2, window_y/3))
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    quit()    

create_aliens()

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                start = True
            if event.key == pygame.K_ESCAPE:
                start = False
            if event.key == pygame.K_p:
                paused = True
            if event.key == pygame.K_c:
                paused = False

    if not water_obs:
        alien_cooldown = 800 #milisecs
    else:
        alien_cooldown = 400 #milisecs

    if not start:
        game_window.blit(start_background, (0,0))
        game_window.blit(text, (window_x/2 - (text.get_width()-10)/2, window_y/8))
        game_window.blit(text1, (10, window_y - text1.get_height() - 70))
        game_window.blit(text2, (10, window_y - text2.get_height() - 40))
        game_window.blit(text3, (10, window_y - text3.get_height() - 10))
    if start:
        if paused:
            continue

        #Set cooldown for alien's bullets
        time_now = pygame.time.get_ticks()
        if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < max(5, levels) and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = Alien_Bullet(attacking_alien.rect.centerx, attacking_alien.rect.bottom, bom)
            alien_bullet_group.add(alien_bullet)
            #Fire balls obs
            if fire_obs and len(fire_group) < (wave_length+levels)*2:
                for i in range(1,wave_length+1):
                    fire_ball = Alien_Bullet((window_x/(wave_length+1))*i, random.choice([-32, -48, -64, -96, -128]), fire_bullet)
                    fire_group.add(fire_ball)
            last_alien_shot = pygame.time.get_ticks()

        #Reset obs when turn new waves
        if len(alien_group) == 0:
            fire_obs = False
            water_obs = False
            spaceship.snow = False
            spaceship.wind = False
            levels += 1
            create_aliens()
            create_obs()

        game_window.blit(gameplay_background, (0,0))
        show_score()

        #Update spaceship
        spaceship.update()

        #Update groups
        bullet_group.update()
        alien_group.update()
        alien_bullet_group.update()
        explosion_group.update()
        bonus_group.update()
        obstacle_group.update()
        fire_group.update()

        #Draw sprite groups
        obstacle_group.draw(game_window)
        fire_group.draw(game_window)
        bonus_group.draw(game_window)
        explosion_group.draw(game_window)
        alien_bullet_group.draw(game_window)
        alien_group.draw(game_window)
        bullet_group.draw(game_window)
        spaceship_group.draw(game_window)

    clock.tick(fps)
    pygame.display.update()
pygame.quit()