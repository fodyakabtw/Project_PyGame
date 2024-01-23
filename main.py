import pygame
import sys
import os
from PIL import Image

pygame.init()


def change_size(size, name):
    image = Image.open(name)
    image = image.resize(size)
    image.save(name)
    return name


SIZE = WIDTH, HEIGHT = 1280, 800
FPS = 60
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_icon(pygame.image.load('data/icon.png'))
background_image = pygame.image.load(change_size(SIZE, 'data/background.png'))
pygame.display.set_caption('The Legend of a Kingdom')
# Загрузка и установка своего курсора
cursor = pygame.image.load("data/cursor.png")
pygame.mouse.set_visible(False)


def pause():
    print("ПАУЗА")
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False

    pygame.display.update()
    clock.tick(15)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением {fullname} не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_images = {'wall': load_image('wall.png'), 'empty': load_image('grass.png'),
               'a': load_image('abroad.png'), '1': load_image('upper_left_corner.png'),
               '2': load_image('left_wall.png'), '3': load_image('lower_left_corner.png'),
               '4': load_image('bottom_wall.png'), '5': load_image('lower_right_corner.png'),
               '6': load_image('right_wall.png'), '7': load_image('upper_right_corner.png'),
               '8': load_image('top_wall.png'), 't': load_image('tree.png')}
player_image = load_image('cat.png')
enemies_images = {'s': load_image('slime_idle.png')}
tile_width = tile_height = 200
move_up = [load_image('up/up1.png'), load_image('up/up2.png'), load_image('up/up3.png'),
           load_image('up/up4.png'), load_image('up/up5.png'), load_image('up/up6.png'),
           load_image('up/up7.png'), load_image('up/up8.png')]
move_left = [load_image('left/left1.png'), load_image('left/left2.png'),
             load_image('left/left3.png'), load_image('left/left4.png'),
             load_image('left/left5.png'), load_image('left/left6.png'),
             load_image('left/left7.png')]
move_right = [load_image('right/right1.png'), load_image('right/right2.png'),
              load_image('right/right3.png'), load_image('right/right4.png'),
              load_image('right/right5.png'), load_image('right/right6.png'),
              load_image('right/right7.png')]
move_down = [load_image('down/down1.png'), load_image('down/down2.png'),
             load_image('down/down3.png'), load_image('down/down4.png'),
             load_image('down/down5.png')]


def terminate():
    pygame.quit()
    sys.exit()


def load_level(file):
    file = f'data/{file}'
    with open(file, 'r') as f:
        map_level = list(map(str.strip, f.readlines()))
    max_width = max(map(len, map_level))
    return list(map(lambda x: x.ljust(max_width, '.'), map_level))


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, object):
        object.rect = object.rect.move(self.dx, self.dy)

    def update(self, target):
        self.dx = WIDTH // 2 - target.rect.x - target.rect.w // 2
        self.dy = HEIGHT // 2 - target.rect.y - target.rect.h // 2


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, enemy):
        super().__init__(all_sprites, enemies_group)
        self.frames = []
        self.columns = columns
        self.enemy = enemy
        self.attack = False
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.pos = x, y
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.attack and self.cur_frame == len(self.frames) - 1:
            self.frames = []
            if self.enemy == 'player':
                self.cut_sheet(load_image('idle.png'), 12, 1)
                self.rect = self.rect.move(self.pos)
                self.cur_frame = 0
                self.attack = False
            else:
                self.cut_sheet(load_image('slime_idle.png'), 5, 1)
                self.rect = self.rect.move(self.pos)
                self.cur_frame = 0
                self.attack = False
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pox_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pox_y


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wall_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pos_y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = pygame.image.load("data/down/down1.png")
        self.pos_x, self.pos_y = tile_width * pos_x + 13, tile_height * pos_y + 5
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x + 13, tile_height * pos_y + 5
        self.status = ''
        self.hero_image_number_up = 0
        self.hero_image_number_down = 0
        self.hero_image_number_right = 0
        self.hero_image_number_left = 0

    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        self.pos_x, self.pos_y = self.pos_x + x, self.pos_y + y
        if (pygame.sprite.spritecollideany(self, wall_group) or
                pygame.sprite.spritecollideany(self, enemies_group)):
            self.rect = self.rect.move(-x, -y)
            self.pos_x, self.pos_y = self.pos_x - x, self.pos_y - y

    def input(self):
        self.status = False
        key = pygame.key.get_pressed()
        if key[pygame.K_s]:
            self.move(0, 25)
            self.status = 'down'
        if key[pygame.K_w]:
            self.move(0, -25)
            self.status = 'up'
        if key[pygame.K_a]:
            self.move(-25, 0)
            self.status = 'left'
        if key[pygame.K_d]:
            self.move(25, 0)
            self.status = 'right'

    def get_status(self):
        return self.status

    def get_rect(self):
        return self.pos_x, self.pos_y

    def update(self, player_status):
        if self.hero_image_number_up > 6:
            self.hero_image_number_up = 0
        if self.hero_image_number_down >= 4:
            self.hero_image_number_down = 0
        if self.hero_image_number_right > 4:
            self.hero_image_number_right = 0
        if self.hero_image_number_left > 4:
            self.hero_image_number_left = 0

        if player_status == 'up':
            self.hero_image_number_up += 1
            self.image = move_up[self.hero_image_number_up % 7]
        elif player_status == 'down':
            self.hero_image_number_down += 1
            self.image = move_down[self.hero_image_number_down % 6]
        elif player_status == 'right':
            self.hero_image_number_right += 1
            self.image = move_right[self.hero_image_number_right % 6]
        elif player_status == 'left':
            self.hero_image_number_left += 1
            self.image = move_left[self.hero_image_number_left % 4]


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == 's':
                Tile('empty', x, y)
                AnimatedSprite(load_image('slime_idle.png'), 5, 1, tile_width * x,
                               tile_height * y, "slime")
            elif level[y][x] in ['a', '1', '2', '3', '4', '5', '6', '7', '8', 't']:
                Wall(level[y][x], x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
camera = Camera()
STEP = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением {fullname} не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class ImageButton:  # Воспомогательный класс для загрузки кнопок на основное окно
    def __init__(self, x, y, width, height, text, image_path, hover_image_path=None,
                 sound_path=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.hover_image = self.image
        if hover_image_path:
            self.hover_image = pygame.image.load(hover_image_path)
            self.hover_image = pygame.transform.scale(self.hover_image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.sound = None
        if sound_path:
            self.sound = pygame.mixer.Sound(sound_path)
        self.is_hovered = False

    def set_pos(self, x, y=None):
        self.x = x
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):  # Отрисовка кнопок и текста на них
        current_image = self.hover_image if self.is_hovered else self.image
        screen.blit(current_image, self.rect.topleft)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):  # Если если столкновение mouse_pos с кнопкой, то True
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):  # Отслеживание нажатия кнопки меню
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.sound:
                self.sound.play()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))


# Воспомогательная функция изменения разрешения окна игры.
def change_video_mode(w, h, fullscreen=0):
    global screen, SIZE, WIDTH, HEIGHT, background_image
    SIZE = WIDTH, HEIGHT = w, h
    screen = pygame.display.set_mode(SIZE, fullscreen)
    background_image = pygame.image.load(change_size(SIZE, 'data/background.png'))


# Функция основного меню игры:
def main_menu():
    # Кнопки
    play_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 252, 75, "",
                              "data/start.png", "data/start_hover.png",
                              "sounds/knopka.mp3")
    settings_button = ImageButton(WIDTH / 2 - (252 / 2), 250, 252, 74, "",
                                  "data/settings.png",
                                  "data/settings_hover.png",
                                  "sounds/knopka.mp3")
    store_button = ImageButton(WIDTH / 2 - (252 / 2), 325, 252, 74, "",
                               "data/store.png",
                               "data/store_hover.png", "sounds/knopka.mp3")
    quit_button = ImageButton(WIDTH / 2 - (252 / 2), 400, 252, 74, "",
                              "data/quit.png",
                              "data/qui_hovert.png", "sounds/knopka.mp3")
    btn = [play_button, settings_button, store_button, quit_button]  # Добавление кнопок в список
    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.USEREVENT and event.button == play_button:
                print('НАЖАТА КНОПКА "play_button"')
                fade()
                game()

            if event.type == pygame.USEREVENT and event.button == settings_button:
                print('НАЖАТА КНОПКА "settings_button"')
                fade()
                settings_menu()

            if event.type == pygame.USEREVENT and event.button == store_button:
                print('НАЖАТА КНОПКА "store_button"')

            if event.type == pygame.USEREVENT and event.button == quit_button:
                print('НАЖАТА КНОПКА "quit_button"')
                running = False
                pygame.quit()
                sys.exit()

            for but in btn:
                but.handle_event(event)

        for but in btn:
            but.set_pos(WIDTH / 2 - (252 / 2))
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)

        # Отрисовка курсора в текущей позиции мыши !нужно делать в каждой фукнции перед флипом!
        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


def settings_menu():
    # Создание кнопок
    audio_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 252, 74, "Звук",
                               "data/back.png",
                               "data/back_border.png", "sounds/knopka.mp3")
    video_button = ImageButton(WIDTH / 2 - (252 / 2), 249, 252, 75, "Графика",
                               "data/back.png",
                               "data/back_border.png", "sounds/knopka.mp3")
    back_button = ImageButton(WIDTH / 2 - (252 / 2), 324, 252, 75, "Назад",
                              "data/back.png",
                              "data/back_border.png", "sounds/knopka.mp3")
    btn = [audio_button, video_button, back_button]

    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                fade()
                main_menu()

            if event.type == pygame.USEREVENT and event.button == back_button:
                print('НАЖАТА КНОПКА "back_button"')
                fade()
                main_menu()

            if event.type == pygame.USEREVENT and event.button == video_button:
                print('НАЖАТА КНОПКА "video_button"')
                fade()
                video_settings()

            for but in btn:
                but.handle_event(event)

        for but in btn:
            but.set_pos(WIDTH / 2 - (252 / 2))
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


# Функция настроек графики. Выбор разрешения окна игры.
def video_settings():
    # Создание кнопок:
    video1_button = ImageButton(WIDTH / 2 - (252 / 2), 175, 175, 74, "960x600",
                                "data/back.png",
                                "data/back_border.png",
                                "sounds/knopka.mp3")
    video2_button = ImageButton(WIDTH / 2 - (252 / 2), 249, 175, 74, "1280x800",
                                "data/back.png",
                                "data/back_border.png",
                                "sounds/knopka.mp3")
    video3_button = ImageButton(WIDTH / 2 - (252 / 2), 323, 175, 74, "Full HD",
                                "data/back.png",
                                "data/back_border.png",
                                "sounds/knopka.mp3")
    video_back_button = ImageButton(WIDTH / 2 - (252 / 2), 397, 175, 74,
                                    "Назад",
                                    "data/back.png",
                                    "data/back_border.png",
                                    "sounds/knopka.mp3")
    btn = [video1_button, video2_button, video3_button, video_back_button]
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background_image, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("VIDEO SETTINGS", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                fade()
                settings_menu()

            if event.type == pygame.USEREVENT and event.button == video1_button:
                print('НАЖАТА КНОПКА "video1_button"')
                change_video_mode(1068, 600)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video2_button:
                print('НАЖАТА КНОПКА "video2_button"')
                change_video_mode(1424, 800)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video3_button:
                print('НАЖАТА КНОПКА "video3_button (FULL HD)"')
                change_video_mode(1920, 1080, pygame.FULLSCREEN)
                fade()
                running = False

            if event.type == pygame.USEREVENT and event.button == video_back_button:
                print('НАЖАТА КНОПКА "video_back_button"')
                fade()
                settings_menu()

            for but in btn:
                but.handle_event(event)

        for but in btn:
            but.set_pos(WIDTH / 2 - (252 / 2))
            but.check_hover(pygame.mouse.get_pos())
            but.draw(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


def sound_settings():
    pass


def new_game():
    # Создание кнопок если понадобятся

    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))

        font = pygame.font.Font(None, 72)
        text_surface = font.render("Добро пожаловать в игру!", True,
                                   (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                fade()
                main_menu()

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x, y))

        pygame.display.flip()


def game():
    screen1 = pygame.display.set_mode((WIDTH, HEIGHT))
    player, level_x, level_y = generate_level(load_level('lvl1.txt'))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                wall_group.empty(), tiles_group.empty(), enemies_group.empty(), player_group.empty()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause()
        player.input()
        player.update(player.get_status())
        camera.update(player)
        screen1.fill('black')
        for sprite in all_sprites:
            camera.apply(sprite)
        wall_group.draw(screen1)
        tiles_group.draw(screen1)
        enemies_group.draw(screen1)
        enemies_group.update()
        player_group.draw(screen1)
        clock.tick(15)
        pygame.display.flip()


# Затемнение, переход между экранами
def fade():
    running = True
    fade_alpha = 0  #

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

        fade_alpha += 5
        if fade_alpha >= 105:
            fade_alpha = 255
            running = False

        pygame.display.flip()
        clock.tick(FPS)


def battle():
    screen2 = pygame.display.set_mode(SIZE)
    run = True
    bow_img = load_image("bow.png")
    numbs = [load_image("one.png"), load_image("two.png")]
    health = load_image("100hp.png")
    bow_btn = ImageButton(220, 40, 80, 80, "",
                          'data/bow.png')
    sword_img = load_image("sword.png")
    sword_btn = ImageButton(320, 40, 80, 80, "",
                            'data/sword.png')
    btns = [bow_btn, sword_btn]
    background = pygame.image.load(change_size(SIZE, 'data/battle_background.png'))
    clock = pygame.time.Clock()
    player_idle = AnimatedSprite(load_image('idle.png'), 12, 1, 160, 250, 'player')
    slime_idle = AnimatedSprite(load_image('slime_idle.png'), 5, 1, 480, 210, 'slime')
    while run:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_2 and not player_idle.attack:
                player_idle.frames = []
                player_idle.cut_sheet(load_image('attack_sword.png'), 8, 1)
                player_idle.rect = player_idle.rect.move(160, 250)
                player_idle.cur_frame = 0
                player_idle.attack = True
                slime_idle.frames = []
                slime_idle.cut_sheet(load_image('slime_attack.png'), 9, 1)
                slime_idle.rect = player_idle.rect.move(320, -35)
                slime_idle.cur_frame = 0
                slime_idle.attack = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1 and not player_idle.attack:
                player_idle.frames = []
                player_idle.cut_sheet(load_image('attack_bow.png'), 5, 1)
                player_idle.rect = player_idle.rect.move(160, 250)
                player_idle.cur_frame = 0
                player_idle.attack = True
        screen2.blit(background, (0, 0))
        screen2.blit(health, (10, 40))
        for btn in btns:
            btn.draw(screen2)
        k = 0
        for element in numbs:
            screen2.blit(element, (220 + k, 120))
            k += 100
        all_sprites.draw(screen2)
        all_sprites.update()
        pygame.display.flip()


main_menu()
